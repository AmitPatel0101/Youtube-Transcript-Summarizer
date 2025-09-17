#!/usr/bin/env python3
"""
Simple script to create basic icons for the Chrome extension
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a red circle background (YouTube red)
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill=(255, 0, 0, 255))
    
    # Draw transcript lines (white)
    line_width = max(1, size // 16)
    line_spacing = size // 8
    start_y = size // 3
    
    for i in range(3):
        y = start_y + (i * line_spacing)
        line_length = size - (2 * margin) - (i * margin // 2)
        draw.rectangle([margin + margin//2, y, margin + margin//2 + line_length, y + line_width], fill=(255, 255, 255, 255))
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    # Create icons directory if it doesn't exist
    os.makedirs('.', exist_ok=True)
    
    # Create different sized icons
    sizes = [16, 48, 128]
    
    for size in sizes:
        filename = f'icon{size}.png'
        create_icon(size, filename)
    
    print("All icons created successfully!")
    print("Note: You need PIL (Pillow) installed: pip install Pillow")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("PIL (Pillow) not found. Install it with: pip install Pillow")
        print("Or create your own 16x16, 48x48, and 128x128 PNG icons manually.")