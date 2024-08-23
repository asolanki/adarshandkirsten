from fastapi import FastAPI, Request, Form, HTTPException, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import shutil
from PIL import Image
from app.scripts.process_images import process_image

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

POSTS_FILE = 'data/posts.json'
UPLOAD_DIR = 'frontend/img/raw'
FULL_DIR = 'frontend/img/full'
THUMB_DIR = 'frontend/img/thumb'

class Media(BaseModel):
    type: str
    content: Optional[str]
    img_name: Optional[str]
    video_name: Optional[str]
    fullsize: Optional[str]
    thumbnail: Optional[str]
    caption: Optional[str]

class Post(BaseModel):
    id: int
    title: str
    date: str
    description: str
    filename: str
    folder: str
    media: List[Media]

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    posts = load_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/add", response_class=HTMLResponse)
async def add_post_form(request: Request):
    return templates.TemplateResponse("add_post.html", {"request": request})

@app.post("/add")
async def add_post(
    title: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    filename: str = Form(...),
    folder: str = Form(...),
    content: str = Form(...),
    files: List[UploadFile] = File(...)
):
    new_post = Post(
        type="media",
        title=title,
        date=date,
        description=description,
        filename=filename,
        folder=folder,
        media=[]
    )

    os.makedirs(os.path.join(UPLOAD_DIR, folder), exist_ok=True)

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        fullsize, thumbnail = process_image(UPLOAD_DIR, FULL_DIR, THUMB_DIR, folder, file.filename)
        new_post.media.append(Media(
            type="image",
            img_name=file.filename,
            fullsize=fullsize,
            thumbnail=thumbnail,
            caption=""
        ))

    # Process content and add text media
    for line in content.split('\n'):
        if line.strip():
            new_post.media.append(Media(type="text", content=line.strip()))

    posts = load_posts()
    posts.append(new_post.dict())
    save_posts(posts)
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit/{post_id}", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int):
    posts = load_posts()
    if post_id < 0 or post_id >= len(posts):
        raise HTTPException(status_code=404, detail="Post not found")
    post = posts[post_id]
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post, "post_id": post_id})

@app.post("/edit/{post_id}")
async def edit_post(
    post_id: int,
    title: str = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    filename: str = Form(...),
    folder: str = Form(...),
    content: str = Form(...),
    files: List[UploadFile] = File(...)
):
    posts = load_posts()
    if post_id < 0 or post_id >= len(posts):
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts[post_id]
    post.update({
        "title": title,
        "date": date,
        "description": description,
        "filename": filename,
        "folder": folder,
        "media": []
    })

    os.makedirs(os.path.join(UPLOAD_DIR, folder), exist_ok=True)

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        fullsize, thumbnail = process_image(UPLOAD_DIR, FULL_DIR, THUMB_DIR, folder, file.filename)
        post["media"].append(Media(
            type="image",
            img_name=file.filename,
            fullsize=fullsize,
            thumbnail=thumbnail,
            caption=""
        ).dict())

    # Process content and add text media
    for line in content.split('\n'):
        if line.strip():
            if line.startswith('[Image:'):
                # This is an existing image, skip it as we've already processed new uploads
                continue
            post["media"].append(Media(type="text", content=line.strip()).dict())

    save_posts(posts)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=92422)