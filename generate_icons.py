from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, path):
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    
    # Draw a rounded rect
    border_rad = size // 6
    d.rounded_rectangle([(0,0), (size-1, size-1)], border_rad, fill=(67, 97, 238), outline=(43, 61, 200), width=max(1, size//16))
    
    # Draw a magnifying glass
    cx, cy = size * 0.4, size * 0.4
    r = size * 0.2
    d.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline='white', width=max(1, size//12))
    
    # Draw handle
    d.line([(cx+r*0.7, cy+r*0.7), (size*0.8, size*0.8)], fill='white', width=max(2, size//8))
    
    # Save the image
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

create_icon(128, 'extension/icons/icon128.png')
create_icon(48, 'extension/icons/icon48.png')
create_icon(16, 'extension/icons/icon16.png')
print("Icons created successfully.")
