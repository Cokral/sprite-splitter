from PIL import Image
import io


def detect_grid(image_bytes):
    # This is a placeholder function. In a real-world scenario,
    # you'd implement more sophisticated image analysis here.
    # For now, we'll just return a default 2x2 grid
    return 2, 2


def split_image(image_bytes, rows, cols):
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    sprite_width = width // cols
    sprite_height = height // rows

    sprites = []

    for i in range(rows):
        for j in range(cols):
            box = (
                j * sprite_width,
                i * sprite_height,
                (j + 1) * sprite_width,
                (i + 1) * sprite_height,
            )
            sprite = img.crop(box)

            # Save sprite to memory
            img_byte_arr = io.BytesIO()
            sprite.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()

            sprites.append(
                {"row": i + 1, "col": j + 1, "filename": f"sprite_{i+1}_{j+1}.png"}
            )

    return sprites
