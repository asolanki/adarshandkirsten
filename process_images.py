# first convert HEICS: 
# for file in *.HEIC; do ffmpeg -i "$file" "${file%.HEIC}.jpg"; done

import os
from PIL import Image
from pillow_heif import register_heif_opener
register_heif_opener()

def process_images(input_dir, output_dir, thumbnail_dir):
    for filename in os.listdir(input_dir):
        # skip non-image files
        if not (filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.heic'))):
            continue

        jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
        jpeg_filepath = os.path.join(output_dir, jpeg_filename)
        thumbnail_filename = os.path.splitext(filename)[0] + '_thumb' + '.jpg'
        thumbnail_filepath = os.path.join(thumbnail_dir, thumbnail_filename)
        
        # Check if image has been processed already
        if os.path.exists(jpeg_filepath) and os.path.exists(thumbnail_filepath):
            print(f'Skipping {filename}, already processed.')
            continue
        
        # Open the image file
        with Image.open(os.path.join(input_dir, filename)) as img:
            # Convert to JPEG
            jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
            jpeg_filepath = os.path.join(output_dir, jpeg_filename)
            img.convert('RGB').save(jpeg_filepath)
            print(f'Saved {jpeg_filepath}')

            # Create thumbnail
            create_thumbnail(img, thumbnail_filepath)

def create_thumbnail(img, thumbnail_filepath):
    # Maintain aspect ratio
    width, height = img.size
    target_width, target_height = 200, 150
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height

    if aspect_ratio > target_aspect_ratio:
        # Crop width, maintain height
        new_width = int(height * target_aspect_ratio)
        left_offset = (width - new_width) // 2
        img_cropped = img.crop((left_offset, 0, left_offset + new_width, height))
    else:
        # Crop height, maintain width
        new_height = int(width / target_aspect_ratio)
        top_offset = (height - new_height) // 2
        img_cropped = img.crop((0, top_offset, width, top_offset + new_height))
    
    # Resize to target dimensions
    img_thumbnail = img_cropped.resize((target_width, target_height), Image.ANTIALIAS)
    
    # Save thumbnail
    os.makedirs(os.path.dirname(thumbnail_filepath), exist_ok=True)
    img_thumbnail.save(thumbnail_filepath)
    print(f'Saved thumbnail {thumbnail_filepath}')

# Directories
input_dir = 'img/raw'
output_dir = 'img/full'
thumbnail_dir = 'img/thumb'

process_images(input_dir, output_dir, thumbnail_dir)
