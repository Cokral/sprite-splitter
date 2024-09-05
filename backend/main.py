import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import zipfile
import tempfile

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FRONTEND_URL = [
    "https://thomascoquereau.com/sprite-splitter/",
    "https://thomascoquereau.com/",
    "https://Cokral.github.io",
    "https://Cokral.github.io/sprite-splitter/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "https://sprite-splitter.onrender.com/",
]
app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URL,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Image Splitter API is running"}


@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.info(f"Response Status: {response.status_code}")
    return response


# Create a directory to store split images
UPLOAD_DIR = "split_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def split_image(
    image_bytes, rows: int, cols: int, original_filename: str, user_id: str
) -> list[dict]:
    """
    Split an image into a grid of rows x cols sprites

    Returns:
        A list of dictionaries, each containing the row, column, and filename of the sprite.
    """
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    sprite_width = width // cols
    sprite_height = height // rows

    sprites = []
    user_dir = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Remove file extension from original filename
    base_filename = os.path.splitext(original_filename)[0]

    for i in range(rows):
        for j in range(cols):
            box = (
                j * sprite_width,
                i * sprite_height,
                (j + 1) * sprite_width,
                (i + 1) * sprite_height,
            )
            sprite = img.crop(box)

            # Save sprite to disk
            filename = f"{base_filename}_row{i+1}_col{j+1}.png"
            filepath = os.path.join(user_dir, filename)
            sprite.save(filepath)

            sprites.append({"row": i + 1, "col": j + 1, "filename": filename})

    return sprites


@app.options("/split")
@app.post("/split")
async def split_image_route(
    request: Request,
    image: UploadFile = File(None),
    rows: int = Form(None),
    cols: int = Form(None),
    x_user_id: str = Header(None),
) -> dict[str, list[dict]]:
    """
    API endpoint that accepts an image file and splits it into a grid of rows x cols sprites.

    Returns:
        A dictionary of sprites, each containing the row, column, and filename of the sprite.
    """
    if request.method == "OPTIONS":
        return {}  # Return an empty dict for OPTIONS requests

    if not image or rows is None or cols is None or not x_user_id:
        raise HTTPException(status_code=400, detail="Missing required fields")

    contents = await image.read()
    sprites = split_image(contents, rows, cols, image.filename, x_user_id)
    return {"sprites": sprites}


@app.get("/download")
async def download_sprites(x_user_id: str = Header(...)):
    """
    Download all split images for a given user as a ZIP file.
    """
    user_dir = os.path.join(UPLOAD_DIR, x_user_id)
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="No images found for this user")

    # Create a temporary zip file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        with zipfile.ZipFile(temp_zip, "w") as zip_file:
            for filename in os.listdir(user_dir):
                file_path = os.path.join(user_dir, filename)
                zip_file.write(file_path, filename)

    # Return the zip file
    return FileResponse(
        temp_zip.name, media_type="application/zip", filename="split_images.zip"
    )


# Optional: Add a cleanup route to delete old files (you might want to run this periodically)
@app.post("/cleanup")
async def cleanup_old_files():
    for user_id in os.listdir(UPLOAD_DIR):
        user_dir = os.path.join(UPLOAD_DIR, user_id)
        if os.path.isdir(user_dir):
            for filename in os.listdir(user_dir):
                file_path = os.path.join(user_dir, filename)
                os.remove(file_path)
            os.rmdir(user_dir)
    return {"message": "Cleanup completed"}
