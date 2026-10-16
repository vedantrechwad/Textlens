import time
import urllib.parse
import requests
import nltk

LABEL_HINTS = {
    "PERSON": "person",
    "ORG": "company organization",
    "GPE": "place",
    "LOC": "location",
    "EVENT": "event",
    "PRODUCT": "product",
    "WORK_OF_ART": "artwork creative work",
    "NORP": "nationality group",
    "FAC": "building facility"
}

ALLOWED_LABELS = set(LABEL_HINTS.keys())

# In-memory cache: (name.lower(), label) -> (timestamp, result)
_CACHE = {}
CACHE_TTL = 24 * 3600  # 24 hours in seconds

USER_AGENT = "Textlens/1.0 (academic NLP project; contact: <placeholder>)"
TIMEOUT_SECONDS = 4


def extract_first_sentence(extract: str) -> str:
    """
    Extracts the first sentence from text using nltk.sent_tokenize.
    Guards against abbreviations (e.g., 'St.', 'Dr.') by falling back
    to the first 200 characters cut at a word boundary if the first
    sentence is under 20 characters.
    """
    if not extract or not extract.strip():
        return ""

    clean_extract = extract.strip()
    try:
        sentences = nltk.sent_tokenize(clean_extract)
    except Exception:
        sentences = [clean_extract]

    if not sentences:
        return ""

    first = sentences[0].strip()

    # Guard against abbreviations if first sentence is under 20 chars and more text exists
    if len(first) < 20 and len(clean_extract) > len(first):
        if len(clean_extract) <= 200:
            first = clean_extract
        else:
            cut = clean_extract[:200]
            last_space = cut.rfind(' ')
            if last_space > 0:
                first = cut[:last_space].rstrip() + "..."
            else:
                first = cut + "..."

    return first


def _fetch_summary_by_title(title: str, headers: dict) -> tuple[int, dict]:
    """
    Fetches Wikipedia page summary by title.
    Returns (status_code, json_dict or {}).
    """
    formatted_title = title.strip().replace(' ', '_')
    quoted_title = urllib.parse.quote(formatted_title, safe=':/')
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted_title}"

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        if resp.status_code == 200:
            return resp.status_code, resp.json()
        return resp.status_code, {}
    except requests.RequestException:
        return 0, {}


def _search_title(query: str, headers: dict) -> str | None:
    """
    Searches Wikipedia titles using the search API.
    Returns top result title/key or None.
    """
    quoted_query = urllib.parse.quote(query)
    url = f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={quoted_query}&limit=1"
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("pages", [])
            if pages and isinstance(pages, list) and len(pages) > 0:
                return pages[0].get("key") or pages[0].get("title")
    except requests.RequestException:
        pass
    return None


def get_entity_summary(name: str, label: str | None = None) -> dict:
    """
    Fetches a 1-sentence quick fact from the Wikipedia REST API for an entity.
    Cached in-memory with a 24-hour TTL.
    """
    if not name or not name.strip():
        return {"found": False}

    clean_name = name.strip()
    cache_key = (clean_name.lower(), label)

    # Check cache
    now = time.time()
    if cache_key in _CACHE:
        ts, cached_result = _CACHE[cache_key]
        if now - ts < CACHE_TTL:
            return cached_result

    headers = {"User-Agent": USER_AGENT}

    status, data = _fetch_summary_by_title(clean_name, headers)

    # Handle disambiguation
    if status == 200 and data.get("type") == "disambiguation":
        hint = LABEL_HINTS.get(label, "") if label else ""
        search_query = f"{clean_name} {hint}".strip() if hint else clean_name
        top_title = _search_title(search_query, headers)
        if top_title:
            status, data = _fetch_summary_by_title(top_title, headers)
            if status == 200 and data.get("type") == "disambiguation":
                result = {"found": False, "reason": "ambiguous"}
                _CACHE[cache_key] = (now, result)
                return result
        else:
            result = {"found": False, "reason": "ambiguous"}
            _CACHE[cache_key] = (now, result)
            return result

    if status != 200 or not data:
        result = {"found": False}
        _CACHE[cache_key] = (now, result)
        return result

    extract = data.get("extract", "")
    fact = extract_first_sentence(extract)

    thumbnail = None
    if isinstance(data.get("thumbnail"), dict):
        thumbnail = data["thumbnail"].get("source")

    page_url = None
    if isinstance(data.get("content_urls"), dict):
        desktop = data["content_urls"].get("desktop")
        if isinstance(desktop, dict):
            page_url = desktop.get("page")

    result = {
        "found": True,
        "title": data.get("title", clean_name),
        "description": data.get("description"),
        "fact": fact,
        "thumbnail": thumbnail,
        "url": page_url
    }

    _CACHE[cache_key] = (now, result)
    return result
