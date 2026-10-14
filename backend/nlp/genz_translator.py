"""
Gen-Z Lingo and Internet Slang Decoder Module for Textlens.
Detects Gen-Z / Internet slang and acronyms, provides plain English definitions,
and translates sentences into Standard English while preserving punctuation and casing.
"""

import re
from typing import Dict, List, Tuple, Any

# Comprehensive dictionary of 150+ Gen-Z slang, internet terms, and idioms.
GENZ_DICTIONARY: Dict[str, Dict[str, Any]] = {
    # Long Multi-Word Idioms (Matched first)
    "ate and left no crumbs": {
        "translation": "performed flawlessly",
        "definition": "Executed something with absolute perfection and excellence.",
        "category": "Praise & Approval",
        "sentiment_score": 2.8
    },
    "left no crumbs": {
        "translation": "did an exceptional job",
        "definition": "Completely succeeded without leaving room for improvement.",
        "category": "Praise & Approval",
        "sentiment_score": 2.5
    },
    "understood the assignment": {
        "translation": "did exactly what was needed with great skill",
        "definition": "Met and exceeded expectations in execution.",
        "category": "Praise & Approval",
        "sentiment_score": 2.6
    },
    "main character energy": {
        "translation": "confident and charismatic presence",
        "definition": "Acting with distinct charisma and self-assurance, as if the protagonist of a story.",
        "category": "Identity",
        "sentiment_score": 2.2
    },
    "main character": {
        "translation": "charismatic protagonist",
        "definition": "Someone radiating self-confidence and natural spotlight.",
        "category": "Identity",
        "sentiment_score": 2.0
    },
    "living rent free": {
        "translation": "constantly occupying one's thoughts",
        "definition": "Unable to stop thinking about a person or idea without any effort on their part.",
        "category": "Obsession",
        "sentiment_score": -0.8
    },
    "rent free": {
        "translation": "constantly on one's mind",
        "definition": "Constantly thought about without effort.",
        "category": "Obsession",
        "sentiment_score": -0.8
    },
    "bombastic side eye": {
        "translation": "extremely judgmental look",
        "definition": "A dramatic look of deep judgment, suspicion, or disapproval.",
        "category": "Reaction",
        "sentiment_score": -2.0
    },
    "side eye": {
        "translation": "skeptical glance",
        "definition": "A suspicious, judgmental, or questioning look.",
        "category": "Reaction",
        "sentiment_score": -1.4
    },
    "touch grass": {
        "translation": "go outside and reconnect with reality",
        "definition": "Advice to step away from screens and the internet to regain perspective.",
        "category": "Advice",
        "sentiment_score": -1.5
    },
    "caught in 4k": {
        "translation": "caught with indisputable evidence",
        "definition": "Busted doing something wrong with clear digital or visual proof.",
        "category": "Accountability",
        "sentiment_score": -1.8
    },
    "spill the tea": {
        "translation": "share the gossip and secrets",
        "definition": "Reveal interesting facts, rumors, or secrets.",
        "category": "Conversation",
        "sentiment_score": 0.8
    },
    "what's the tea": {
        "translation": "what is the latest gossip",
        "definition": "Asking for the latest news or secrets.",
        "category": "Conversation",
        "sentiment_score": 0.5
    },
    "vibe check": {
        "translation": "assessing the mood and energy",
        "definition": "Checking whether someone has good intentions or positive energy.",
        "category": "Social",
        "sentiment_score": 0.8
    },
    "hits different": {
        "translation": "feels exceptionally special and impactful",
        "definition": "Has a unique, superior emotional or sensory resonance.",
        "category": "Experience",
        "sentiment_score": 2.3
    },
    "out of pocket": {
        "translation": "wildly inappropriate and erratic",
        "definition": "Behaving in an unexpectedly unhinged or inappropriate manner.",
        "category": "Behavior",
        "sentiment_score": -2.0
    },
    "we are so back": {
        "translation": "things have dramatically improved",
        "definition": "Expression of supreme optimism and triumphant comeback.",
        "category": "Optimism",
        "sentiment_score": 2.6
    },
    "it's so over": {
        "translation": "everything has failed",
        "definition": "Expression of absolute defeat, hopeless doom, or failure.",
        "category": "Pessimism",
        "sentiment_score": -2.7
    },
    "let him cook": {
        "translation": "give him space to demonstrate his talent",
        "definition": "Allow someone the freedom and time to do what they do best.",
        "category": "Encouragement",
        "sentiment_score": 2.0
    },
    "let her cook": {
        "translation": "give her space to demonstrate her talent",
        "definition": "Allow someone the freedom and time to do what they do best.",
        "category": "Encouragement",
        "sentiment_score": 2.0
    },
    "let bro cook": {
        "translation": "give him space to demonstrate his talent",
        "definition": "Allow someone the freedom and time to do what they do best.",
        "category": "Encouragement",
        "sentiment_score": 2.0
    },
    "let them cook": {
        "translation": "give them space to demonstrate their skills",
        "definition": "Allowing someone to proceed without interference.",
        "category": "Encouragement",
        "sentiment_score": 2.0
    },
    "he is cooking": {
        "translation": "he is doing something brilliant",
        "definition": "Performing exceptionally or having a breakthrough idea.",
        "category": "Praise",
        "sentiment_score": 2.2
    },
    "fanum tax": {
        "translation": "taking a portion of someone's food",
        "definition": "Humorous internet meme for taking food from a friend without asking.",
        "category": "Humor & Meme",
        "sentiment_score": 0.0
    },
    "crash out": {
        "translation": "lose all self-control in reckless anger",
        "definition": "To recklessly self-destruct or act impulsively in extreme frustration.",
        "category": "Anger",
        "sentiment_score": -2.7
    },
    "crashed out": {
        "translation": "lost all self-control in reckless anger",
        "definition": "Lost composure and acted recklessly out of fury.",
        "category": "Anger",
        "sentiment_score": -2.7
    },
    "crashing out": {
        "translation": "losing all self-control in reckless anger",
        "definition": "In the process of an uncontrollable reckless outburst.",
        "category": "Anger",
        "sentiment_score": -2.7
    },
    "say less": {
        "translation": "understood completely",
        "definition": "Understood without needing any further explanation.",
        "category": "Agreement",
        "sentiment_score": 1.5
    },
    "no cap": {
        "translation": "truthfully and honestly",
        "definition": "Not lying; completely authentic and real.",
        "category": "Truthfulness",
        "sentiment_score": 1.6
    },
    "real talk": {
        "translation": "speaking completely honestly",
        "definition": "Being earnest and genuine.",
        "category": "Truthfulness",
        "sentiment_score": 1.3
    },
    "big yikes": {
        "translation": "extremely embarrassing and uncomfortable",
        "definition": "A severe reaction of second-hand embarrassment or alarm.",
        "category": "Reaction",
        "sentiment_score": -2.2
    },
    "it's giving": {
        "translation": "it exudes the vibe of",
        "definition": "Suggests a specific atmosphere, aesthetic, or resemblance.",
        "category": "Description",
        "sentiment_score": 1.0
    },
    "is giving": {
        "translation": "radiates the vibe of",
        "definition": "Emits a particular aesthetic, tone, or energy.",
        "category": "Description",
        "sentiment_score": 1.0
    },
    "completely giving": {
        "translation": "completely radiating the vibe of",
        "definition": "Exuding a distinctive aesthetic or presence.",
        "category": "Description",
        "sentiment_score": 1.0
    },
    "down bad": {
        "translation": "pathetically desperate for affection",
        "definition": "Experiencing intense, desperate attraction or romantic longing.",
        "category": "Romance",
        "sentiment_score": -1.5
    },
    "locked in": {
        "translation": "intensely focused and dedicated",
        "definition": "Concentrated with maximum effort and laser focus.",
        "category": "Productivity",
        "sentiment_score": 2.3
    },
    "lock in": {
        "translation": "focus with maximum intensity",
        "definition": "Get serious and eliminate all distractions.",
        "category": "Productivity",
        "sentiment_score": 2.0
    },
    "glow up": {
        "translation": "dramatic positive transformation",
        "definition": "A significant personal, physical, or stylistic improvement.",
        "category": "Improvement",
        "sentiment_score": 2.5
    },
    "glow-up": {
        "translation": "dramatic positive transformation",
        "definition": "A significant personal, physical, or stylistic improvement.",
        "category": "Improvement",
        "sentiment_score": 2.5
    },
    "pop off": {
        "translation": "express oneself passionately or succeed vigorously",
        "definition": "To excel spectacularly or unleash emotional energy.",
        "category": "Excitement",
        "sentiment_score": 2.0
    },
    "stand on business": {
        "translation": "take full responsibility and back words with action",
        "definition": "Backing up words with decisive action and integrity.",
        "category": "Integrity",
        "sentiment_score": 2.2
    },
    "it's an absolute serve": {
        "translation": "it is an exceptionally stunning look",
        "definition": "A complete, flawless fashion or visual triumph.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.9
    },
    "it’s an absolute serve": {
        "translation": "it is an exceptionally stunning look",
        "definition": "A complete, flawless fashion or visual triumph.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.9
    },
    "an absolute serve": {
        "translation": "an exceptionally stunning look",
        "definition": "Looking completely impeccable and stylish.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.8
    },
    "absolute serve": {
        "translation": "exceptionally stunning look",
        "definition": "Delivering an outstandingly attractive presentation.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.8
    },
    "it's a serve": {
        "translation": "it is a stunning look",
        "definition": "An impressive, stylish outfit or presentation.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.5
    },
    "it’s a serve": {
        "translation": "it is a stunning look",
        "definition": "An impressive, stylish outfit or presentation.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.5
    },
    "a serve": {
        "translation": "a stunning look",
        "definition": "An impressive outfit or confident aesthetic.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.5
    },
    "serving looks": {
        "translation": "delivering striking style",
        "definition": "Consistently showing off stunning fashion and visual appeal.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.6
    },
    "serving face": {
        "translation": "looking extraordinarily attractive",
        "definition": "Displaying striking facial features and modeling confidence.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.7
    },
    "unspoken rizz": {
        "translation": "effortless natural charm",
        "definition": "Magnetic attraction without even saying a word.",
        "category": "Romance & Charm",
        "sentiment_score": 2.6
    },
    "rizz up": {
        "translation": "charm and flirt with",
        "definition": "To charm, flirt with, or seduce someone.",
        "category": "Romance & Charm",
        "sentiment_score": 2.2
    },
    "rizzed up": {
        "translation": "charmed and flirted with",
        "definition": "Successfully charmed or flirted with someone.",
        "category": "Romance & Charm",
        "sentiment_score": 2.2
    },
    "w rizz": {
        "translation": "flawless romantic charm",
        "definition": "Winning charisma and smooth conversational skills.",
        "category": "Romance & Charm",
        "sentiment_score": 2.5
    },
    "l rizz": {
        "translation": "awkward lack of charm",
        "definition": "Poor or cringe flirting attempts.",
        "category": "Romance & Charm",
        "sentiment_score": -2.0
    },
    "aura points": {
        "translation": "coolness and respect points",
        "definition": "Metaphorical score of one's personal charisma and swagger.",
        "category": "Social Standing",
        "sentiment_score": 1.5
    },
    "+1000 aura": {
        "translation": "massive boost in coolness",
        "definition": "Achieving something that drastically elevates respect.",
        "category": "Social Standing",
        "sentiment_score": 2.5
    },
    "-1000 aura": {
        "translation": "embarrassing loss of coolness",
        "definition": "Suffering a humiliating setback that loses social respect.",
        "category": "Social Standing",
        "sentiment_score": -2.5
    },
    "lost aura": {
        "translation": "lost respect and coolness",
        "definition": "Suffered a decrease in admiration or composure.",
        "category": "Social Standing",
        "sentiment_score": -2.0
    },
    "goes hard": {
        "translation": "is exceptionally impressive",
        "definition": "Possesses incredible energy, quality, or aesthetic impact.",
        "category": "Praise & Approval",
        "sentiment_score": 2.5
    },
    "go hard": {
        "translation": "be exceptionally impressive",
        "definition": "Perform with intense quality and vigor.",
        "category": "Praise & Approval",
        "sentiment_score": 2.4
    },
    "slaps hard": {
        "translation": "is extremely enjoyable",
        "definition": "Incredible music or food with immense flavor or beat.",
        "category": "Praise & Approval",
        "sentiment_score": 2.4
    },
    "ate that": {
        "translation": "did that exceptionally well",
        "definition": "Handled or presented something with flawless execution.",
        "category": "Praise & Approval",
        "sentiment_score": 2.6
    },
    "she ate": {
        "translation": "she did exceptionally well",
        "definition": "She excelled and dominated in performance or style.",
        "category": "Praise & Approval",
        "sentiment_score": 2.6
    },
    "he ate": {
        "translation": "he did exceptionally well",
        "definition": "He excelled and dominated in performance or style.",
        "category": "Praise & Approval",
        "sentiment_score": 2.6
    },
    "they ate": {
        "translation": "they did exceptionally well",
        "definition": "They excelled and dominated in performance or style.",
        "category": "Praise & Approval",
        "sentiment_score": 2.6
    },
    "fumbled the bag": {
        "translation": "ruined a priceless opportunity",
        "definition": "Lost out on massive success or wealth through foolishness.",
        "category": "Failure",
        "sentiment_score": -2.6
    },
    "fumble the bag": {
        "translation": "ruin a priceless opportunity",
        "definition": "Lose out on a major opportunity through poor choices.",
        "category": "Failure",
        "sentiment_score": -2.5
    },
    "fumbled": {
        "translation": "messed up a great opportunity",
        "definition": "Ruined a chance with a person or goal.",
        "category": "Failure",
        "sentiment_score": -2.2
    },
    "red flag": {
        "translation": "major warning sign",
        "definition": "An alarming indicator of toxic or unhealthy behavior.",
        "category": "Relationships",
        "sentiment_score": -2.5
    },
    "green flag": {
        "translation": "positive healthy sign",
        "definition": "A reassuring indicator of mature, healthy character.",
        "category": "Relationships",
        "sentiment_score": 2.4
    },
    "beige flag": {
        "translation": "quirky but harmless idiosyncrasy",
        "definition": "An odd or unusual trait in someone that isn't good or bad.",
        "category": "Relationships",
        "sentiment_score": 0.0
    },
    "sending me": {
        "translation": "making me laugh uncontrollably",
        "definition": "Causing overwhelming amusement or laughter.",
        "category": "Humor",
        "sentiment_score": 2.0
    },
    "im dead": {
        "translation": "laughing hysterically",
        "definition": "Hyperbolic expression of laughter.",
        "category": "Humor",
        "sentiment_score": 2.0
    },
    "i'm dead": {
        "translation": "laughing hysterically",
        "definition": "Hyperbolic expression of laughter.",
        "category": "Humor",
        "sentiment_score": 2.0
    },
    "gas up": {
        "translation": "enthusiastically boost someone's ego",
        "definition": "Complementing someone to make them feel confident.",
        "category": "Encouragement",
        "sentiment_score": 2.0
    },
    "gassing up": {
        "translation": "boosting someone's ego with compliments",
        "definition": "Building up someone's confidence.",
        "category": "Encouragement",
        "sentiment_score": 2.0
    },
    "put me on": {
        "translation": "introduced me to something great",
        "definition": "Recommended or exposed someone to a high-quality song, place, or thing.",
        "category": "Recommendation",
        "sentiment_score": 2.0
    },
    "massive w": {
        "translation": "monumental victory",
        "definition": "A tremendous success or positive event.",
        "category": "Success",
        "sentiment_score": 2.8
    },
    "huge w": {
        "translation": "huge victory",
        "definition": "A major success.",
        "category": "Success",
        "sentiment_score": 2.6
    },
    "massive l": {
        "translation": "monumental defeat",
        "definition": "A devastating loss or embarrassing setback.",
        "category": "Defeat",
        "sentiment_score": -2.8
    },
    "huge l": {
        "translation": "huge defeat",
        "definition": "A major loss or mistake.",
        "category": "Defeat",
        "sentiment_score": -2.6
    },
    "take the l": {
        "translation": "accept defeat gracefully",
        "definition": "Acknowledge that you lost or were wrong.",
        "category": "Defeat",
        "sentiment_score": -1.8
    },
    "valid af": {
        "translation": "extremely justified and impressive",
        "definition": "Completely agreeable, cool, or warranted.",
        "category": "Validation",
        "sentiment_score": 2.4
    },
    "real af": {
        "translation": "deeply genuine and truthful",
        "definition": "Strikingly honest and authentic.",
        "category": "Truthfulness",
        "sentiment_score": 2.0
    },
    "clean fit": {
        "translation": "sharp and stylish outfit",
        "definition": "A well-coordinated, neat, and fashionable clothing combination.",
        "category": "Fashion",
        "sentiment_score": 2.4
    },
    "your fit": {
        "translation": "your outfit",
        "definition": "Your clothing style and ensemble.",
        "category": "Fashion",
        "sentiment_score": 1.5
    },
    "the fit": {
        "translation": "the outfit",
        "definition": "The clothing and style ensemble.",
        "category": "Fashion",
        "sentiment_score": 1.5
    },
    "fire fit": {
        "translation": "amazing outfit",
        "definition": "An exceptionally stylish ensemble.",
        "category": "Fashion",
        "sentiment_score": 2.5
    },
    "on god": {
        "translation": "I swear truthfully",
        "definition": "Solemn oath of absolute honesty.",
        "category": "Emphasis",
        "sentiment_score": 1.2
    },

    # Single-Word Terms & Core Slang
    "fit": {
        "translation": "outfit",
        "definition": "Clothing style or ensemble (short for outfit).",
        "category": "Fashion",
        "sentiment_score": 1.2
    },
    "fits": {
        "translation": "outfits",
        "definition": "Clothing styles or ensembles.",
        "category": "Fashion",
        "sentiment_score": 1.2
    },
    "serve": {
        "translation": "stunning look",
        "definition": "Delivering an exceptional, breathtaking aesthetic presentation.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.5
    },
    "serving": {
        "translation": "delivering a stunning look",
        "definition": "Exuding supreme beauty, confidence, or style.",
        "category": "Fashion & Approval",
        "sentiment_score": 2.5
    },
    "giving": {
        "translation": "radiating the vibe of",
        "definition": "Evoking a distinct aura, tone, or impression.",
        "category": "Description",
        "sentiment_score": 1.0
    },
    "aura": {
        "translation": "charisma and coolness",
        "definition": "A distinct quality of personal presence, swagger, or prestige.",
        "category": "Social Standing",
        "sentiment_score": 1.8
    },
    "rizz": {
        "translation": "charm and charisma",
        "definition": "Ability to charm and romantically attract others (short for charisma).",
        "category": "Romance & Charm",
        "sentiment_score": 2.3
    },
    "rizzing": {
        "translation": "charming",
        "definition": "Using charm or flirtatious charisma.",
        "category": "Romance & Charm",
        "sentiment_score": 2.0
    },
    "rizzler": {
        "translation": "master of charisma",
        "definition": "Someone with exceptional charisma and flirtatious charm.",
        "category": "Romance & Charm",
        "sentiment_score": 2.3
    },
    "bussin": {
        "translation": "exceptionally delicious and great",
        "definition": "Extremely tasty, enjoyable, or high quality.",
        "category": "Praise & Approval",
        "sentiment_score": 2.7
    },
    "bussing": {
        "translation": "exceptionally delicious and great",
        "definition": "Extremely good or tasty.",
        "category": "Praise & Approval",
        "sentiment_score": 2.7
    },
    "delulu": {
        "translation": "delusional and unrealistic",
        "definition": "Holding unrealistic, fanciful, or stubbornly optimistic illusions.",
        "category": "Psychology & Humor",
        "sentiment_score": -1.2
    },
    "solulu": {
        "translation": "solution",
        "definition": "Humorous wordplay meaning a solution (often paired with delulu).",
        "category": "Humor",
        "sentiment_score": 1.0
    },
    "slay": {
        "translation": "excel brilliantly",
        "definition": "To perform outstandingly well or look stunning.",
        "category": "Praise & Approval",
        "sentiment_score": 2.8
    },
    "slayed": {
        "translation": "excelled brilliantly",
        "definition": "Performed with extraordinary style or skill.",
        "category": "Praise & Approval",
        "sentiment_score": 2.8
    },
    "slaying": {
        "translation": "excelling brilliantly",
        "definition": "Performing with supreme style and confidence.",
        "category": "Praise & Approval",
        "sentiment_score": 2.8
    },
    "cap": {
        "translation": "lie",
        "definition": "A falsehood, exaggeration, or untrue claim.",
        "category": "Deception",
        "sentiment_score": -2.0
    },
    "capping": {
        "translation": "lying",
        "definition": "Telling a falsehood or exaggerating.",
        "category": "Deception",
        "sentiment_score": -2.0
    },
    "sus": {
        "translation": "suspicious",
        "definition": "Questionable, untrustworthy, or doubtful.",
        "category": "Skepticism",
        "sentiment_score": -1.8
    },
    "mid": {
        "translation": "mediocre and unimpressive",
        "definition": "Average, subpar, or not worth the hype.",
        "category": "Criticism",
        "sentiment_score": -1.8
    },
    "cooked": {
        "translation": "in deep trouble or ruined",
        "definition": "In an irreversible state of failure, trouble, or extreme fatigue.",
        "category": "Doom & Failure",
        "sentiment_score": -2.5
    },
    "brainrot": {
        "translation": "mind-numbing internet nonsense",
        "definition": "Low-quality, repetitive digital content that dulls the mind.",
        "category": "Internet Culture",
        "sentiment_score": -2.2
    },
    "sigma": {
        "translation": "independent and self-reliant",
        "definition": "A solitary, self-sufficient person who operates outside social hierarchies.",
        "category": "Archetype",
        "sentiment_score": 1.2
    },
    "yap": {
        "translation": "babble pointlessly",
        "definition": "Talk excessively without saying anything meaningful.",
        "category": "Communication",
        "sentiment_score": -1.5
    },
    "yapping": {
        "translation": "talking excessively about trivia",
        "definition": "Babbling on and on without substance.",
        "category": "Communication",
        "sentiment_score": -1.5
    },
    "yapper": {
        "translation": "excessive chatterbox",
        "definition": "Someone who talks incessantly without substance.",
        "category": "Communication",
        "sentiment_score": -1.4
    },
    "mewing": {
        "translation": "jawline tongue exercises",
        "definition": "Holding tongue against roof of mouth to supposedly sharpen jawline.",
        "category": "Trend",
        "sentiment_score": 0.0
    },
    "gyatt": {
        "translation": "expression of awe or surprise",
        "definition": "An emphatic exclamation (short for 'god damn').",
        "category": "Exclamation",
        "sentiment_score": 1.0
    },
    "gyat": {
        "translation": "expression of awe or surprise",
        "definition": "An emphatic exclamation.",
        "category": "Exclamation",
        "sentiment_score": 1.0
    },
    "skibidi": {
        "translation": "absurd meme trend",
        "definition": "Viral nonsensical meme word from popular animated web series.",
        "category": "Internet Meme",
        "sentiment_score": 0.0
    },
    "deadass": {
        "translation": "completely seriously",
        "definition": "Speaking with absolute seriousness and genuine intent.",
        "category": "Emphasis",
        "sentiment_score": 1.2
    },
    "fr": {
        "translation": "for real",
        "definition": "Truly, genuinely, or without exaggeration.",
        "category": "Emphasis",
        "sentiment_score": 1.0
    },
    "frfr": {
        "translation": "truly and genuinely",
        "definition": "Deeply sincere emphasis; for real, for real.",
        "category": "Emphasis",
        "sentiment_score": 1.2
    },
    "ong": {
        "translation": "I swear on god",
        "definition": "An oath affirming that one is telling the absolute truth.",
        "category": "Emphasis",
        "sentiment_score": 1.1
    },
    "lowkey": {
        "translation": "subtly or secretly",
        "definition": "To a mild, understated, or discreet degree.",
        "category": "Tone",
        "sentiment_score": 0.0
    },
    "highkey": {
        "translation": "overtly and unapologetically",
        "definition": "Intensely, openly, and without concealment.",
        "category": "Tone",
        "sentiment_score": 0.5
    },
    "finna": {
        "translation": "about to",
        "definition": "Fixing to / intending to do something.",
        "category": "Intention",
        "sentiment_score": 0.0
    },
    "opps": {
        "translation": "rivals and opponents",
        "definition": "Opposition or adversaries.",
        "category": "Conflict",
        "sentiment_score": -1.8
    },
    "opp": {
        "translation": "opponent or rival",
        "definition": "An adversary.",
        "category": "Conflict",
        "sentiment_score": -1.8
    },
    "sheesh": {
        "translation": "wow, incredible",
        "definition": "Exclamation of awe, disbelief, or hype.",
        "category": "Reaction",
        "sentiment_score": 1.8
    },
    "ratio": {
        "translation": "outvoted with negative replies",
        "definition": "When replies drastically outnumber likes, indicating rejection.",
        "category": "Social Media",
        "sentiment_score": -2.0
    },
    "drip": {
        "translation": "stylish fashion and outfit",
        "definition": "Exceptional clothing style, swagger, or appearance.",
        "category": "Fashion",
        "sentiment_score": 2.3
    },
    "drippy": {
        "translation": "exceptionally fashionable",
        "definition": "Having great fashion and aesthetic taste.",
        "category": "Fashion",
        "sentiment_score": 2.2
    },
    "goated": {
        "translation": "the greatest of all time",
        "definition": "Unmatched in quality, talent, or status.",
        "category": "Praise & Approval",
        "sentiment_score": 3.0
    },
    "goat": {
        "translation": "greatest of all time",
        "definition": "The undisputed best in a discipline.",
        "category": "Praise & Approval",
        "sentiment_score": 2.9
    },
    "npc": {
        "translation": "person lacking independent thought",
        "definition": "Someone perceived as having predictable, conformist behavior.",
        "category": "Criticism",
        "sentiment_score": -2.0
    },
    "based": {
        "translation": "unapologetically authentic and admirable",
        "definition": "Remaining true to one's convictions regardless of what others think.",
        "category": "Praise & Approval",
        "sentiment_score": 2.2
    },
    "cringe": {
        "translation": "embarrassing and awkward",
        "definition": "Causing feelings of intense discomfort or embarrassment.",
        "category": "Criticism",
        "sentiment_score": -2.2
    },
    "the ick": {
        "translation": "sudden feeling of repulsion",
        "definition": "A sudden aversion to someone after a specific behavior.",
        "category": "Repulsion",
        "sentiment_score": -2.2
    },
    "ick": {
        "translation": "sudden feeling of disgust",
        "definition": "A sudden turn-off in attraction.",
        "category": "Repulsion",
        "sentiment_score": -2.1
    },
    "glazing": {
        "translation": "over-flattering and sycophantic praise",
        "definition": "Excessively complimenting or sucking up to someone.",
        "category": "Criticism",
        "sentiment_score": -1.7
    },
    "glaze": {
        "translation": "excessively flatter",
        "definition": "Flatter excessively.",
        "category": "Criticism",
        "sentiment_score": -1.6
    },
    "stan": {
        "translation": "devoted super-fan",
        "definition": "An obsessive or fiercely dedicated fan of a person or brand.",
        "category": "Fandom",
        "sentiment_score": 1.2
    },
    "stanning": {
        "translation": "fiercely supporting as a fan",
        "definition": "Adoring or passionately championing a celebrity or cause.",
        "category": "Fandom",
        "sentiment_score": 1.3
    },
    "ghosted": {
        "translation": "abruptly cut off all communication",
        "definition": "Suddenly stopped responding to messages without any explanation.",
        "category": "Dating & Social",
        "sentiment_score": -2.3
    },
    "ghosting": {
        "translation": "abruptly ignoring someone",
        "definition": "Ceasing all communication without warning.",
        "category": "Dating & Social",
        "sentiment_score": -2.2
    },
    "clout": {
        "translation": "social influence and fame",
        "definition": "Online popularity, followers, or social standing.",
        "category": "Social Media",
        "sentiment_score": 1.1
    },
    "flex": {
        "translation": "boast or show off",
        "definition": "To flaunt wealth, achievements, or attributes.",
        "category": "Ego",
        "sentiment_score": 0.5
    },
    "flexing": {
        "translation": "showing off boastfully",
        "definition": "Flaunting one's advantages or luxuries.",
        "category": "Ego",
        "sentiment_score": 0.5
    },
    "simp": {
        "translation": "person excessively submissive to someone they like",
        "definition": "Someone who does far too much for an unreciprocated romantic interest.",
        "category": "Romance",
        "sentiment_score": -1.5
    },
    "simping": {
        "translation": "groveling for romantic attention",
        "definition": "Overly subservient behavior toward a crush.",
        "category": "Romance",
        "sentiment_score": -1.5
    },
    "situationship": {
        "translation": "ambiguous romantic relationship",
        "definition": "An undefined romantic partnership lacking commitment.",
        "category": "Romance",
        "sentiment_score": -0.8
    },
    "unhinged": {
        "translation": "wildly erratic and chaotic",
        "definition": "Behaving with unpredictable, crazy energy.",
        "category": "Behavior",
        "sentiment_score": -1.2
    },
    "twin": {
        "translation": "like-minded best friend",
        "definition": "A close companion who shares identical thoughts and styles.",
        "category": "Friendship",
        "sentiment_score": 2.0
    },
    "bestie": {
        "translation": "best friend",
        "definition": "A cherished close friend.",
        "category": "Friendship",
        "sentiment_score": 1.8
    },
    "motion": {
        "translation": "financial momentum and success",
        "definition": "Having verifiable accomplishments, cash flow, and social traction.",
        "category": "Success",
        "sentiment_score": 2.3
    },
    "mog": {
        "translation": "outshine physically",
        "definition": "Looking visibly more physically attractive than someone next to you.",
        "category": "Appearance",
        "sentiment_score": 1.5
    },
    "mogging": {
        "translation": "physically outshining others",
        "definition": "Dominating in physical aesthetic appeal.",
        "category": "Appearance",
        "sentiment_score": 1.5
    },
    "snack": {
        "translation": "very attractive person",
        "definition": "Someone who looks extraordinarily appealing.",
        "category": "Romance",
        "sentiment_score": 2.0
    },
    "snatched": {
        "translation": "looking impeccably stylish and fit",
        "definition": "Looking exceptionally sharp, fit, or fashionable.",
        "category": "Fashion",
        "sentiment_score": 2.4
    },
    "slaps": {
        "translation": "is exceptionally good",
        "definition": "Possesses incredible energy or quality (often music or food).",
        "category": "Praise & Approval",
        "sentiment_score": 2.3
    },
    "bop": {
        "translation": "catchy and enjoyable song",
        "definition": "An exceptionally good, rhythmic track.",
        "category": "Music & Entertainment",
        "sentiment_score": 2.2
    },
    "valid": {
        "translation": "completely understandable and justified",
        "definition": "Reasonable, acceptable, or logically sound.",
        "category": "Validation",
        "sentiment_score": 1.9
    },
    "tea": {
        "translation": "gossip and juicy scoop",
        "definition": "Inside scoop, rumors, or dramatic revelations.",
        "category": "Conversation",
        "sentiment_score": 0.5
    },
    "salty": {
        "translation": "bitter and irritated",
        "definition": "Resentful or angry over a minor defeat or slight.",
        "category": "Emotion",
        "sentiment_score": -1.8
    },
    "shook": {
        "translation": "deeply shocked and astonished",
        "definition": "Emotionally shaken or stunned by an occurrence.",
        "category": "Emotion",
        "sentiment_score": -1.0
    },
    "boujee": {
        "translation": "luxurious and high-class",
        "definition": "Possessing expensive, opulent, or bourgeois taste.",
        "category": "Lifestyle",
        "sentiment_score": 1.2
    },
    "bougie": {
        "translation": "luxurious and high-class",
        "definition": "Possessing lavish or high-end taste.",
        "category": "Lifestyle",
        "sentiment_score": 1.2
    },
    "cheugy": {
        "translation": "outdated and trying too hard",
        "definition": "Out of touch with contemporary aesthetic trends.",
        "category": "Criticism",
        "sentiment_score": -1.6
    },
    "unc": {
        "translation": "older gentleman",
        "definition": "An older man who displays traditional or outdated habits.",
        "category": "Age & Social",
        "sentiment_score": 0.0
    },
    "tweaking": {
        "translation": "behaving erratically or hyperactively",
        "definition": "Acting crazy, irrational, or paranoid.",
        "category": "Behavior",
        "sentiment_score": -2.0
    },
    "gatekeep": {
        "translation": "withhold information to stay exclusive",
        "definition": "Limiting others from discovering something enjoyable or useful.",
        "category": "Social",
        "sentiment_score": -1.5
    },
    "gatekeeping": {
        "translation": "withholding secrets to stay exclusive",
        "definition": "Deliberately concealing tips or sources to stay unique.",
        "category": "Social",
        "sentiment_score": -1.5
    },
    "gaslight": {
        "translation": "psychologically manipulate someone to doubt reality",
        "definition": "Manipulating someone into doubting their own sanity, memory, or perception.",
        "category": "Manipulation",
        "sentiment_score": -2.9
    },
    "gaslighting": {
        "translation": "psychologically manipulating reality",
        "definition": "Manipulating someone to doubt their own senses.",
        "category": "Manipulation",
        "sentiment_score": -2.9
    },
    "era": {
        "translation": "distinct chapter in life",
        "definition": "A defined personal phase or aesthetic identity.",
        "category": "Identity",
        "sentiment_score": 1.0
    },
    "af": {
        "translation": "extremely",
        "definition": "Emphatic intensifier (as fuck).",
        "category": "Emphasis",
        "sentiment_score": 0.8
    },
    "asf": {
        "translation": "extremely",
        "definition": "Emphatic intensifier.",
        "category": "Emphasis",
        "sentiment_score": 0.8
    },
    "iykyk": {
        "translation": "if you know, you know",
        "definition": "An inside joke or reference understood only by an in-group.",
        "category": "Slang Acronym",
        "sentiment_score": 0.5
    },
    "ngl": {
        "translation": "not going to lie",
        "definition": "Speaking honestly and frankly.",
        "category": "Slang Acronym",
        "sentiment_score": 0.5
    },
    "tbh": {
        "translation": "to be honest",
        "definition": "Offering a candid, sincere opinion.",
        "category": "Slang Acronym",
        "sentiment_score": 0.5
    },
    "idk": {
        "translation": "I do not know",
        "definition": "Expressing uncertainty.",
        "category": "Slang Acronym",
        "sentiment_score": 0.0
    },
    "imo": {
        "translation": "in my opinion",
        "definition": "Stating a subjective view.",
        "category": "Slang Acronym",
        "sentiment_score": 0.0
    },
    "imho": {
        "translation": "in my humble opinion",
        "definition": "Stating a humble view.",
        "category": "Slang Acronym",
        "sentiment_score": 0.0
    },
    "smh": {
        "translation": "shaking my head in disappointment",
        "definition": "Disapproval or disbelief at something foolish.",
        "category": "Slang Acronym",
        "sentiment_score": -1.5
    },
    "fwiw": {
        "translation": "for what it is worth",
        "definition": "Offering advice or input modestly.",
        "category": "Slang Acronym",
        "sentiment_score": 0.0
    },
    "periodt": {
        "translation": "and that is final",
        "definition": "Adding finality and absolute emphasis to an argument.",
        "category": "Emphasis",
        "sentiment_score": 1.5
    },
    "period": {
        "translation": "and that is final",
        "definition": "Absolute emphasis ending debate.",
        "category": "Emphasis",
        "sentiment_score": 1.2
    },
    "bet": {
        "translation": "agreed, deal",
        "definition": "Confirmation of agreement or acceptance of a challenge.",
        "category": "Agreement",
        "sentiment_score": 1.5
    },
    "w": {
        "translation": "win",
        "definition": "A triumph, victory, or positive outcome.",
        "category": "Success",
        "sentiment_score": 2.2
    },
    "l": {
        "translation": "loss",
        "definition": "A failure, defeat, or embarrassing setback.",
        "category": "Defeat",
        "sentiment_score": -2.2
    }
}


def _match_casing(original_token: str, replacement: str) -> str:
    """
    Applies the casing style of the original token to the replacement text.
    """
    if original_token.isupper() and len(original_token) > 1:
        return replacement.upper()
    if original_token[0].isupper():
        return replacement.capitalize()
    return replacement.lower()


def _build_regex_pattern(term: str) -> str:
    """
    Creates a regex pattern for a term that supports both ASCII (') and smart (’) apostrophes,
    whitespace variations, and robust word boundaries.
    """
    escaped = re.escape(term)
    # Match both standard and curly apostrophes
    escaped = re.sub(r"\\['’]", r"['’]", escaped)
    # Match arbitrary whitespace between words
    escaped = re.sub(r'\\\s+', r'\\s+', escaped)
    return r'(?<![A-Za-z0-9])' + escaped + r'(?![A-Za-z0-9])'


# Disambiguation Guards for Polysemous / Dual-Use Slang Terms

# 1. 'tea' (Beverage vs Gossip)
BEVERAGE_PRE_REGEX = re.compile(
    r'\b(matcha|iced|ice|hot|cold|warm|green|black|herbal|chai|boba|milk|earl\s+grey|peppermint|chamomile|jasmine|bubble|fruit|lemon|sweet|ginger|mint|oolong|hibiscus|rooibos|darjeeling|sencha|white|loose\s+leaf|cup\s+of|mug\s+of|pot\s+of|glass\s+of|brewing|brew|drank|drinking)\s+$',
    re.IGNORECASE
)
BEVERAGE_POST_REGEX = re.compile(
    r'^\s+\b(bag|bags|leaf|leaves|kettle|pot|cup|latte|tree|plantation)\b',
    re.IGNORECASE
)

# 2. 'cap' / 'capping' (Headwear/Lid vs Lying)
LITERAL_CAP_PRE_REGEX = re.compile(
    r'\b(baseball|bottle|swim|shower|lens|pen|knee|salary|gas|capital|hub|ice|market|fitting)\s+$',
    re.IGNORECASE
)
LITERAL_CAP_POST_REGEX = re.compile(
    r'^\s+\b(hat|size|visor|strap|closure)\b',
    re.IGNORECASE
)

# 3. 'cooked' (Culinary food preparation vs Doomed / ruined)
CULINARY_COOKED_PRE_REGEX = re.compile(
    r'\b(slow|slowly|fresh|freshly|partially|well|fully|properly|evenly|under|over|home|deep|pressure|pan|oven|steam|steamed|flame|wood|kettle|perfectly|lightly|thoroughly|chef|cook|baker|caterer)\s+$',
    re.IGNORECASE
)
CULINARY_COOKED_POST_REGEX = re.compile(
    r'^\s+(for\s+\w+\s+)?(us|me|him|her|them|everyone|someone|friends|family)?\s*'
    r'(a\s+|an\s+|the\s+|some\s+|our\s+|my\s+|his\s+|her\s+|their\s+|fresh\s+|delicious\s+|good\s+|hot\s+|big\s+|nice\s+|tasty\s+)?'
    r'(dinner|lunch|breakfast|meal|food|meat|steak|chicken|pasta|rice|beef|pork|fish|egg|eggs|soup|vegetables|veggies|curry|sauce|potatoes|dish|bacon|turkey|salmon|shrimp|noodles|pizza|burger|burgers|pie|bread|supper|beans|tofu|mushrooms|sausage|lobster|crab|ribs|stew|medium|rare|well-done|well\s+done|thoroughly|evenly|crispy|al\s+dente|at\s+\d+|in\s+the\s+oven|on\s+the\s+stove|with\s+(olive\s+)?oil|with\s+butter|to\s+perfection|for\s+\d+\s+(hours|minutes|mins|hrs))\b',
    re.IGNORECASE
)

# 4. 'fit' / 'fits' (Fitness / sizing vs Outfit)
LITERAL_FIT_PRE_REGEX = re.compile(
    r'\b(stay|staying|keep|keeping|physically|aerobic|cardio|don\'t|doesn\'t|didn\'t|won\'t|can\'t|cannot|tight|snug|perfect|to)\s+$',
    re.IGNORECASE
)
LITERAL_FIT_POST_REGEX = re.compile(
    r'^\s+\b(into|in|together|me|you|him|her|them|through|for)\b',
    re.IGNORECASE
)

# 5. 'mid' (Temporal prefix / middle vs Mediocre)
LITERAL_MID_POST_REGEX = re.compile(
    r'^(?:[-–]\w+|\s+\b(morning|day|afternoon|night|year|season|century|december|january|february|march|april|may|june|july|august|september|october|november)\b)',
    re.IGNORECASE
)

# 6. 'salty' (Salt taste vs Irritated / bitter mood)
LITERAL_SALTY_PRE_REGEX = re.compile(
    r'\b(tastes|tasting|smells|smelling|too|slightly|overly|extra)\s+$',
    re.IGNORECASE
)
LITERAL_SALTY_POST_REGEX = re.compile(
    r'^\s+\b(water|sea|ocean|food|chips|popcorn|pretzel|pretzels|nuts|soup|broth|butter|caramel|cracker|crackers|taste|flavor)\b',
    re.IGNORECASE
)

# 7. 'snack' (Food vs Attractive person)
LITERAL_SNACK_PRE_REGEX = re.compile(
    r'\b(eat|ate|eating|eaten|have|had|having|healthy|quick|midnight|afternoon|morning|sweet|salty|crunchy|fruit|packaged)\s+$',
    re.IGNORECASE
)
LITERAL_SNACK_POST_REGEX = re.compile(
    r'^\s+\b(bar|bars|pack|packs|time|break|food|machine|aisle)\b',
    re.IGNORECASE
)

# 8. 'slaps' (Physical hand strike vs Great song/vibe)
LITERAL_SLAPS_PRE_REGEX = re.compile(
    r'\b(physically|violently|angrily|accidentally)\s+$',
    re.IGNORECASE
)
LITERAL_SLAPS_POST_REGEX = re.compile(
    r'^\s+\b(him|her|me|them|us|his|her|my|the\s+face|the\s+table|the\s+desk|the\s+hand)\b',
    re.IGNORECASE
)

# 9. 'drip' / 'drippy' (Liquid leak vs Fashion swagger)
LITERAL_DRIP_PRE_REGEX = re.compile(
    r'\b(faucet|tap|water|pipe|leak|leaking|oil|rain|coffee|iv|slow|slowly|constant)\s+$',
    re.IGNORECASE
)
LITERAL_DRIP_POST_REGEX = re.compile(
    r'^\s+\b(of\s+water|from\s+the|pan|coffee|drop|drops|leak)\b',
    re.IGNORECASE
)

# 10. 'flex' / 'flexing' (Muscle tensing / bending vs Boasting)
LITERAL_FLEX_POST_REGEX = re.compile(
    r'^\s+(?:his|her|their|my|your)?\s*\b(muscles?|biceps?|joints?|body|wings?|feet|legs?|quads?|abs|spine)\b',
    re.IGNORECASE
)

# 11. 'ratio' (Math proportion vs Social media reply loss)
LITERAL_RATIO_PRE_REGEX = re.compile(
    r'\b(aspect|gear|compression|signal-to-noise|debt-to-income|pe|price-to-earnings|golden|student-to-teacher|mathematical|1:|2:|3:|4:|5:|10:)\s+$',
    re.IGNORECASE
)
LITERAL_RATIO_POST_REGEX = re.compile(
    r'^\s+\b(of\s+\d+|is\s+\d+|to\s+\d+|\d+:\d+)\b',
    re.IGNORECASE
)

# 12. 'bet' (Gambling wager vs Affirmation / deal)
LITERAL_BET_PRE_REGEX = re.compile(
    r'\b(placed|place|placing|make|making|lost|won|sports|casino|poker|dollar|\$)\s+(a\s+)?$',
    re.IGNORECASE
)
LITERAL_BET_POST_REGEX = re.compile(
    r'^\s+(\$|\d+|dollars?|cents?|on\s+the|against|with\s+\w+\s+that)\b',
    re.IGNORECASE
)

# 13. 'shook' (Physical shake vs Astonished)
LITERAL_SHOOK_POST_REGEX = re.compile(
    r'^\s+\b(hands?|his\s+head|her\s+head|my\s+head|their\s+head|the\s+bottle|the\s+can|it\s+up)\b',
    re.IGNORECASE
)

# 14. 'serve' / 'serving' (Food / tennis / military vs Stunning look)
LITERAL_SERVE_POST_REGEX = re.compile(
    r'^\s+\b(the\s+ball|an\s+ace|dinner|lunch|breakfast|food|drinks|the\s+customer|the\s+guests|in\s+the\s+military|in\s+the\s+army|in\s+the\s+navy|time\s+in\s+prison|sentences?)\b',
    re.IGNORECASE
)


def _is_valid_slang_match(term: str, text: str, start: int, end: int) -> bool:
    """
    Validates whether an ambiguous term is genuinely used as slang or as its
    literal everyday English meaning. Returns False if literal context is detected.
    """
    term_lower = term.lower()
    pre_text = text[:start]
    post_text = text[end:]

    if term_lower == "tea":
        if BEVERAGE_PRE_REGEX.search(pre_text) or BEVERAGE_POST_REGEX.search(post_text):
            return False

    elif term_lower in ("cap", "capping"):
        if LITERAL_CAP_PRE_REGEX.search(pre_text) or LITERAL_CAP_POST_REGEX.search(post_text):
            return False

    elif term_lower == "cooked":
        if CULINARY_COOKED_PRE_REGEX.search(pre_text) or CULINARY_COOKED_POST_REGEX.search(post_text):
            return False

    elif term_lower in ("fit", "fits"):
        if LITERAL_FIT_PRE_REGEX.search(pre_text) or LITERAL_FIT_POST_REGEX.search(post_text):
            return False

    elif term_lower == "mid":
        if LITERAL_MID_POST_REGEX.search(post_text):
            return False

    elif term_lower == "salty":
        if LITERAL_SALTY_PRE_REGEX.search(pre_text) or LITERAL_SALTY_POST_REGEX.search(post_text):
            return False

    elif term_lower == "snack":
        if LITERAL_SNACK_PRE_REGEX.search(pre_text) or LITERAL_SNACK_POST_REGEX.search(post_text):
            return False

    elif term_lower == "slaps":
        if LITERAL_SLAPS_PRE_REGEX.search(pre_text) or LITERAL_SLAPS_POST_REGEX.search(post_text):
            return False

    elif term_lower in ("drip", "drippy"):
        if LITERAL_DRIP_PRE_REGEX.search(pre_text) or LITERAL_DRIP_POST_REGEX.search(post_text):
            return False

    elif term_lower in ("flex", "flexing"):
        if LITERAL_FLEX_POST_REGEX.search(post_text):
            return False

    elif term_lower == "ratio":
        if LITERAL_RATIO_PRE_REGEX.search(pre_text) or LITERAL_RATIO_POST_REGEX.search(post_text):
            return False

    elif term_lower == "bet":
        if LITERAL_BET_PRE_REGEX.search(pre_text) or LITERAL_BET_POST_REGEX.search(post_text):
            return False

    elif term_lower == "shook":
        if LITERAL_SHOOK_POST_REGEX.search(post_text):
            return False

    elif term_lower in ("serve", "serving"):
        if LITERAL_SERVE_POST_REGEX.search(post_text):
            return False

    return True


def detect_slang(text: str) -> List[Dict[str, Any]]:
    """
    Scans the text for all known Gen-Z slang terms, prioritizing longer expressions first.
    Returns a list of detected terms with metadata (definition, category, translation, positions).
    """
    if not text or not text.strip():
        return []

    detected = []
    # Sort terms by length in descending order so longer phrases take priority
    sorted_terms = sorted(GENZ_DICTIONARY.keys(), key=lambda k: len(k), reverse=True)
    
    # Track covered character spans to avoid overlapping sub-matches
    matched_spans = []

    for term in sorted_terms:
        pattern = _build_regex_pattern(term)
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            overlap = any(s <= start < e or s < end <= e for s, e in matched_spans)
            if not overlap and _is_valid_slang_match(term, text, start, end):
                matched_spans.append((start, end))
                original_snippet = text[start:end]
                meta = GENZ_DICTIONARY[term]
                detected.append({
                    "term": term,
                    "matched_text": original_snippet,
                    "translation": meta["translation"],
                    "definition": meta["definition"],
                    "category": meta["category"],
                    "sentiment_score": meta["sentiment_score"],
                    "start": start,
                    "end": end
                })

    # Sort detected items by start position
    detected.sort(key=lambda x: x["start"])
    return detected


def decode_genz_text(text: str) -> Dict[str, Any]:
    """
    Detects all Gen-Z slang terms, produces a standard plain English translation,
    and computes a Gen-Z Slang Intensity / Brainrot Index.
    """
    if not text or not text.strip():
        return {
            "original": text,
            "plain_english": text,
            "detected_terms": [],
            "all_spans": [],
            "term_count": 0,
            "has_slang": False,
            "slang_density": 0,
            "slang_level": "Clean Standard English"
        }

    detected = detect_slang(text)
    words = re.findall(r'\b\w+\b', text)
    total_words = max(1, len(words))

    if not detected:
        return {
            "original": text,
            "plain_english": text,
            "detected_terms": [],
            "all_spans": [],
            "term_count": 0,
            "has_slang": False,
            "slang_density": 0,
            "slang_level": "Clean Standard English"
        }

    # Reconstruct text by replacing detected spans from right to left
    translated_chars = list(text)
    for item in sorted(detected, key=lambda x: x["start"], reverse=True):
        start = item["start"]
        end = item["end"]
        original_chunk = text[start:end]
        cased_replacement = _match_casing(original_chunk, item["translation"])
        translated_chars[start:end] = list(cased_replacement)

    plain_english = "".join(translated_chars)

    # Calculate Slang Intensity Score / Brainrot Meter
    slang_count = len(detected)
    density = round((slang_count / total_words) * 100, 1)

    if density >= 25 or slang_count >= 4:
        level = "Ultra Gen-Z / Pure Brainrot (10/10)"
    elif density >= 15 or slang_count >= 3:
        level = "Heavy Gen-Z Slang (8/10)"
    elif density >= 8 or slang_count >= 2:
        level = "Moderate Gen-Z Slang (5/10)"
    else:
        level = "Light Gen-Z Slang (2/10)"

    # Provide clean unique summary of terms for the UI with spans
    unique_terms = []
    term_map = {}
    for item in detected:
        t = item["term"]
        span = [item["start"], item["end"]]
        if t not in term_map:
            term_info = {
                "term": t,
                "matched_text": item["matched_text"],
                "translation": item["translation"],
                "definition": item["definition"],
                "category": item["category"],
                "sentiment_score": item["sentiment_score"],
                "spans": [span],
                "occurrences": 1
            }
            term_map[t] = term_info
            unique_terms.append(term_info)
        else:
            term_map[t]["spans"].append(span)
            term_map[t]["occurrences"] += 1

    return {
        "original": text,
        "plain_english": plain_english,
        "detected_terms": unique_terms,
        "all_spans": [{"term": item["term"], "start": item["start"], "end": item["end"], "matched_text": item["matched_text"]} for item in detected],
        "term_count": slang_count,
        "has_slang": True,
        "slang_density": density,
        "slang_level": level
    }


def get_genz_sentiment_lexicon() -> Dict[str, float]:
    """
    Returns a dictionary of slang terms mapped to sentiment scores (-4.0 to +4.0)
    for injecting into VADER lexicon.
    """
    return {term: meta["sentiment_score"] for term, meta in GENZ_DICTIONARY.items()}
