import cv2
import numpy as np

IMG_SIZE = 224


def _deskew(image: np.ndarray) -> np.ndarray:
    """Correct skew in handwriting using minimum area rectangle on contours.

    Detects the dominant text angle and rotates the image to align text
    horizontally. This improves both CNN accuracy and heuristic analysis
    (baseline alignment, spacing measurements).
    """
    # Work on a binary copy
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find all non-zero pixel coordinates
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 50:
        return image  # Not enough content to estimate skew

    # Fit minimum area bounding rectangle
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]

    # Normalize angle: minAreaRect returns angles in [-90, 0)
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only correct if skew is meaningful but not extreme
    if abs(angle) < 0.5 or abs(angle) > 30:
        return image

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, rotation_matrix, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocess handwriting image for CNN input.

    Pipeline: Grayscale -> CLAHE -> Deskew -> Otsu binarization -> Median blur -> Resize -> Normalize
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

    # Deskew — correct rotated handwriting before feature extraction
    deskewed = _deskew(enhanced)

    # Otsu's binarization
    _, binary = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

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
