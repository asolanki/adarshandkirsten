import os
import sys
from PIL import Image
from pillow_heif import register_heif_opener
import ffmpeg
import argparse

register_heif_opener()

UPLOAD_DIR = '../frontend/img/raw'
FULL_DIR = '../frontend/img/full'
THUMB_DIR = '../frontend/img/thumb'

def process_dir(folder):
    input_dir = os.path.join(UPLOAD_DIR, folder)
    output_dir = os.path.join(FULL_DIR, folder)
    thumbnail_dir = os.path.join(THUMB_DIR, folder)

    for filename in os.listdir(input_dir):
        filetype = filename.lower().split('.')[-1]
        if not (filetype.endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'heic', 'mov'))):
            continue
        
        if filetype == 'mov':
            process_video(input_dir, output_dir, thumbnail_dir, filename)
        else:
            process_image(input_dir, output_dir, thumbnail_dir, filename)

def process_image(input_dir, output_dir, thumbnail_dir, filename):
    jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
    jpeg_filepath = os.path.join(output_dir, jpeg_filename)
    thumbnail_filename = os.path.splitext(filename)[0] + '_thumb.jpg'
    thumbnail_filepath = os.path.join(thumbnail_dir, thumbnail_filename)
    
    # Check if image has been processed already
    if os.path.exists(jpeg_filepath) and os.path.exists(thumbnail_filepath):
        print(f'Skipping {filename}, already processed.')
        return
    
    # Convert to JPEG, create thumbnail
    with Image.open(os.path.join(input_dir, filename)) as img:
        img.convert('RGB').save(jpeg_filepath, quality=85, optimize=True)
        print(f'Saved {jpeg_filepath}')
        create_thumbnail_from_img(img, thumbnail_filepath)

    return f"img/full/{os.path.basename(output_dir)}/{jpeg_filename}", f"img/thumb/{os.path.basename(thumbnail_dir)}/{thumbnail_filename}"

def process_video(input_dir, output_dir, thumbnail_dir, filename):
    mp4_filename = os.path.splitext(filename)[0] + '.mp4'
    mp4_filepath = os.path.join(output_dir, mp4_filename)
    thumbnail_filename = os.path.splitext(filename)[0] + '_thumb.jpg'
    thumbnail_filepath = os.path.join(thumbnail_dir, thumbnail_filename) 

    # Check if video has been processed already
    if os.path.exists(mp4_filepath) and os.path.exists(thumbnail_filepath):
        print(f'Skipping {filename}, already processed.')
        return

    # process proxy video with ffmpeg
    try:
        ffmpeg.input(os.path.join(input_dir, filename)) \
            .output(mp4_filepath, 
                    format='mp4', 
                    vcodec='libx264', 
                    acodec='aac', 
                    pix_fmt='yuv420p', 
                    vf='scale=-2:1080') \
            .run(capture_stdout=True, capture_stderr=True)
    except ffmpeg._run.Error as e:
        print(e.stderr, file=sys.stderr)

    create_thumbnail_from_video(mp4_filepath, thumbnail_filepath)

    return f"img/full/{os.path.basename(output_dir)}/{mp4_filename}", f"img/thumb/{os.path.basename(thumbnail_dir)}/{thumbnail_filename}"

def create_thumbnail_from_img(img, thumbnail_filepath):
    width, height = img.size
    aspect_ratio = width / height
    target_width, target_height = 200, 150
    target_aspect_ratio = target_width / target_height

    # crop either width or height depending on original
    if aspect_ratio > target_aspect_ratio:
        new_width = int(height * target_aspect_ratio)
        left_offset = (width - new_width) // 2
        img_cropped = img.crop((left_offset, 0, left_offset + new_width, height))
    else:
        new_height = int(width / target_aspect_ratio)
        top_offset = (height - new_height) // 2
        img_cropped = img.crop((0, top_offset, width, top_offset + new_height))
    
    # Resize to target dimensions
    img_thumbnail = img_cropped.resize((target_width, target_height), Image.LANCZOS)
    
    # Save thumbnail
    os.makedirs(os.path.dirname(thumbnail_filepath), exist_ok=True)
    img_thumbnail.save(thumbnail_filepath, format='JPEG', quality=85, optimize=True)
    print(f'Saved thumbnail {thumbnail_filepath}')

def create_thumbnail_from_video(video_filepath, thumbnail_filepath):
    # Extract a frame from the video at the halfway point as thumbnail
    video_info = ffmpeg.probe(video_filepath)
    duration = float(video_info['format']['duration'])
    timestamp = duration / 2
    
    extracted_frame_filepath = f'{video_filepath}.frame.jpg'

    try:
        ffmpeg.input(video_filepath, ss=timestamp) \
            .output(extracted_frame_filepath, vframes=1, format='image2', update=1) \
            .run(capture_stdout=True, capture_stderr=True)
    except ffmpeg._run.Error as e:
        print(e.stderr, file=sys.stderr)  

    # Load the extracted frame as an image and create thumbnail
    with Image.open(extracted_frame_filepath) as img:
        create_thumbnail_from_img(img, thumbnail_filepath)
    
    # Remove the extracted frame file since we don't need it anymore
    os.remove(extracted_frame_filepath)

def main(folder_name):
    # Ensure output directories exist
    os.makedirs(os.path.join(FULL_DIR, folder_name), exist_ok=True)
    os.makedirs(os.path.join(THUMB_DIR, folder_name), exist_ok=True)

    process_dir(folder_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images in a specified folder.')
    parser.add_argument('folder_name', help='Name of the folder within img/raw to process.')
    args = parser.parse_args()

    main(args.folder_name)