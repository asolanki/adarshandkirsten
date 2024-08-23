import json
import os
import shutil
from PIL import Image

POSTS_FILE = '../data/posts.json'
UPLOAD_DIR = '../frontend/img/raw'
FULL_DIR = '../frontend/img/full'
THUMB_DIR = '../frontend/img/thumb'

def process_image(folder, filename):
    input_path = os.path.join(UPLOAD_DIR, folder, filename)
    full_path = os.path.join(FULL_DIR, folder, filename)
    thumb_path = os.path.join(THUMB_DIR, folder, f"{os.path.splitext(filename)[0]}_thumb.jpg")

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

    with Image.open(input_path) as img:
        # Save full-size image
        img.save(full_path, quality=85, optimize=True)

        # Create and save thumbnail
        img.thumbnail((200, 200))
        img.save(thumb_path, format='JPEG', quality=85, optimize=True)

    return f"img/full/{folder}/{filename}", f"img/thumb/{folder}/{os.path.splitext(filename)[0]}_thumb.jpg"

def sync_posts():
    with open(POSTS_FILE, 'r') as f:
        posts = json.load(f)

    for post in posts:
        folder = post['folder']
        for media in post['media']:
            if media['type'] == 'image':
                img_name = media['img_name']
                fullsize, thumbnail = process_image(folder, img_name)
                media['fullsize'] = fullsize
                media['thumbnail'] = thumbnail

    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=2)

if __name__ == "__main__":
    sync_posts()