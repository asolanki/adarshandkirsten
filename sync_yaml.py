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
            if post['type'] == 'text':
                print(f'Type = text')
                rendered_html = template.render(
                    title=post['title'],
                    date=post['date'],
                    description=post['description'],
                    content_type='text',
                    content=None,
                    images=None
                )
            elif post['type'] == 'images':
                print(f'Type = images')
                processed_images = [{
                    'fullsize': f'../img/full/{post["folder"]}/{img["img_name"]}.jpg',
                    'thumbnail': f'../img/thumb/{post["folder"]}/{img["img_name"]}_thumb.jpg',
                        'caption': img['caption']
                    } for img in post['images']]

                rendered_html = template.render(
                    title=post['title'],
                    date=post['date'],
                    description=post['description'],
                    content_type='images',
                    content=None,
                    images=processed_images
                )
            else:
                print(f'Error: Unknown post type for {filename}')
                continue
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
