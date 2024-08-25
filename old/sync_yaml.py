import os
import yaml
import json
from jinja2 import Template

##
## INSTRUCTIONS: FIRST ADD POST TO POSTS.YAML
## THEN RUN THIS TO CREATE TEMPLATE
## THEN EDIT THE POST TEMPLATE HTML
## 

# Directory where the posts are stored
post_dir = 'posts/'

# Load posts from YAML
with open('posts.yaml', 'r') as file:
    posts = yaml.safe_load(file)

# Load the HTML template
with open('post_template.html', 'r') as template_file:
    template = Template(template_file.read())

# List all current posts in the directory
current_posts = os.listdir(post_dir)

# Track whether all posts are synced
all_synced = True

print("Starting sync yaml")

# Check each post from YAML
for post in posts:
    filename = post['filename']

    # If the post doesn't exist, create it
    if filename not in current_posts:
        print(f'Creating file: {filename}')
        with open(os.path.join(post_dir, filename), 'w') as file:
            processed_content = []
            for item in post['media']:
                if item['type'] == 'image':
                    base_name, ext = os.path.splitext(item['img_name'])
                    processed_content.append({
                        'type': 'image',
                        'fullsize': f'../img/full/{post["folder"]}/{base_name}{ext}',
                        'thumbnail': f'../img/thumb/{post["folder"]}/{base_name}_thumb{ext}',
                        'caption': item['caption']
                    })
                elif item['type'] == 'video':
                    base_name, ext = os.path.splitext(item['video_name'])
                    processed_content.append({
                        'type': 'video',
                        'fullsize': f'../img/full/{post["folder"]}/{base_name}.mp4',
                        'thumbnail': f'../img/thumb/{post["folder"]}/{base_name}_thumb.jpg',
                        'caption': item['caption']
                    })
                elif item['type'] == 'text':
                    processed_content.append({
                        'type': 'text',
                        'content': item['content']
                    })

            rendered_html = template.render(
                title=post['title'],
                date=post['date'],
                description=post['description'],
                content=processed_content
            )
            file.write(rendered_html)
            print(f'Created file {filename}')
        all_synced = False
    else:
        current_posts.remove(filename)

# Check for untracked posts
if current_posts:
    print('Error: untracked files')
    for post in current_posts:
        print(post)
    all_synced = False

# If all posts are synced
if all_synced:
    print('OK: All posts synced')

# create new json for JS parsing by front-end
with open('posts.json', 'w') as json_file:
    json.dump(posts, json_file, ensure_ascii=False, indent=4)

print("posts.json has been updated")
