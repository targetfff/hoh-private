from PIL import Image


def normalize_pic(filename):
    img = Image.open(filename)
    width, height = img.size
    if width >= height:
        new_height, new_width = height, height
    else:
        new_height, new_width = width, width
    resized = img.resize((new_width, new_height), Image.LANCZOS)
    resized.save("filename", format="png")

