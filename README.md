# A+K Blog Platform
Hand-rolled blog platform for adarshandkirsten.com.  Posts are auto-generated from posts.yaml, images and videos are stored in /img/raw/{post_name}

## How to create a post
1. Determine the short post_name of your post (e.g. "singapore")
2. Create a new folder and upload all images and videos (e.g. /img/raw/singapore).  
3. Edit posts.yaml, create a new blog post for post_name, include any text, images, or videos (in order)
4. Run process_images.py to automatically scale-down images/videos and generate thumbnails
5. Run sync_posts.py to automatically generate the post (will be stored at /posts/{post_name}.html)
6. Push changes to main branch, changes should be autodeployed in a few minutes.

## How to edit a post
1. Determine what the short post_name is by finding the post in /posts or in posts.yaml (e.g "singapore") 
2. Add any new images/videos to/img/{post_name}/raw
3. Edit posts.yaml, adding references to the new images and videos where needed, and adding any text content.
4. Run process_images.py to automatically scale-down images/videos and generate thumbnails
5. Run sync_posts.py to automatically generate the post (will be stored at /posts/{post_name}.html)
6. Push changes to main branch, changes should be autodeployed in a few minutes.