import os


def load_images_from_directory(directory: str) -> list[str]:
    """Returns a list of image file paths."""
    images = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".png"):
            full_path = os.path.join(directory, filename)
            images.append(full_path)
    return images