from PIL import Image
import os

def generate_pwa_icons():
    # Create static/icons directory if it doesn't exist
    icons_dir = os.path.join('static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Open the favicon
    img = Image.open('favicon.ico')
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Define the sizes we need
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Generate each size
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        output_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        resized.save(output_path, 'PNG')
        print(f'Generated {output_path}')

if __name__ == '__main__':
    generate_pwa_icons()
    print('Icon generation complete!') 