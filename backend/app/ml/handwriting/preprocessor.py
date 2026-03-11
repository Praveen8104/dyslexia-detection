import cv2
import numpy as np

IMG_SIZE = 224


def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocess handwriting image for CNN input.

    Pipeline: Grayscale -> CLAHE -> Otsu binarization -> Median blur -> Resize -> Normalize
    Returns: numpy array of shape (224, 224, 1)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE for better contrast normalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Otsu's binarization
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Median blur to reduce noise
    blurred = cv2.medianBlur(binary, 3)

    # Resize to target size
    resized = cv2.resize(blurred, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)

    # Normalize to [0, 1]
    normalized = resized.astype(np.float32) / 255.0

    # Add channel dimension
    return np.expand_dims(normalized, axis=-1)


def preprocess_batch(image_paths: list) -> np.ndarray:
    """Preprocess a batch of images."""
    return np.array([preprocess_image(p) for p in image_paths])
