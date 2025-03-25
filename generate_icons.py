from PIL import Image
import os

def generate_pwa_icons(input_path, output_dir):
    """Generate PWA icons in different sizes from input image."""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the input image
    with Image.open(input_path) as img:
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # Generate each size
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            output_path = os.path.join(output_dir, f'icon-{size}x{size}.png')
            resized.save(output_path, 'PNG')
            print(f'Generated {output_path}')

if __name__ == '__main__':
    input_path = 'favicon.ico'
    output_dir = 'static/icons'
    generate_pwa_icons(input_path, output_dir)
    print('Icon generation complete!') 