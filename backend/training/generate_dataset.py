"""Generate synthetic handwriting dataset for dyslexia detection training.

Creates 3 classes:
- Normal: Clean handwritten text
- Reversal: Letters mirrored/reversed (b↔d, p↔q, s↔z)
- Corrected: Text with strike-throughs, overwriting, messy corrections

Uses OpenCV to render text with handwriting-like distortions.
"""

import os
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "handwriting")
SAMPLES_PER_CLASS = 2000
IMG_SIZE = 256  # Generate larger, resize to 128 during preprocessing
CLASSES = ["Normal", "Reversal", "Corrected"]

# Common words children write
WORDS = [
    "bad", "bed", "big", "boy", "but", "can", "day", "did", "dog", "dad",
    "big", "pat", "pot", "put", "pen", "pad", "bat", "bit", "bud", "bus",
    "dip", "dug", "den", "dim", "dab", "pub", "peg", "pig", "pod", "pop",
    "saw", "sit", "sun", "set", "six", "zip", "zoo", "zap", "nap", "map",
    "the", "and", "was", "for", "are", "his", "her", "she", "has", "had",
    "apple", "table", "paper", "happy", "puppy", "baby", "body", "door",
    "queen", "quick", "speed", "spell", "sleep", "deep", "keep", "been",
]

SENTENCES = [
    "the dog ran", "a big bed", "bad boy", "pop and dad",
    "the sun is up", "she has a pet", "he can run", "a red bus",
]

# Reversal pairs (commonly confused letters)
REVERSAL_MAP = {
    'b': 'd', 'd': 'b', 'p': 'q', 'q': 'p',
    's': 'z', 'z': 's', 'n': 'u', 'u': 'n',
}


def get_font(size=36):
    """Try to get a handwriting-style font, fall back to default."""
    font_paths = [
        "/System/Library/Fonts/Noteworthy.ttc",
        "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
        "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
        "/System/Library/Fonts/MarkerFelt.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def add_noise(img, intensity=0.05):
    """Add salt-and-pepper noise."""
    noise = np.random.random(img.shape)
    img[noise < intensity] = 0
    img[noise > (1 - intensity)] = 255
    return img


def add_distortion(img):
    """Add slight elastic distortion to simulate handwriting variation."""
    rows, cols = img.shape[:2]
    # Random affine transform
    src_pts = np.float32([[0, 0], [cols - 1, 0], [0, rows - 1]])
    jitter = random.randint(3, 10)
    dst_pts = np.float32([
        [random.randint(0, jitter), random.randint(0, jitter)],
        [cols - 1 - random.randint(0, jitter), random.randint(0, jitter)],
        [random.randint(0, jitter), rows - 1 - random.randint(0, jitter)],
    ])
    M = cv2.getAffineTransform(src_pts, dst_pts)
    return cv2.warpAffine(img, M, (cols, rows), borderValue=255)


def add_line_wobble(img):
    """Add slight rotation to simulate tilted writing."""
    rows, cols = img.shape[:2]
    angle = random.uniform(-5, 5)
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    return cv2.warpAffine(img, M, (cols, rows), borderValue=255)


def vary_thickness(img):
    """Randomly dilate or erode to vary stroke thickness."""
    kernel_size = random.choice([1, 2, 3])
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    if random.random() > 0.5:
        return cv2.dilate(img, kernel, iterations=1)
    return cv2.erode(img, kernel, iterations=1)


def render_text(text, font_size=None, offset_y=0):
    """Render text onto a white image using PIL."""
    if font_size is None:
        font_size = random.randint(28, 48)
    font = get_font(font_size)

    img = Image.new("L", (IMG_SIZE, IMG_SIZE), 255)
    draw = ImageDraw.Draw(img)

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Center text with some random offset
    x = max(5, (IMG_SIZE - tw) // 2 + random.randint(-15, 15))
    y = max(5, (IMG_SIZE - th) // 2 + random.randint(-10, 10) + offset_y)

    # Draw with slight gray variation
    color = random.randint(0, 40)
    draw.text((x, y), text, fill=color, font=font)

    return np.array(img)


def generate_normal(idx):
    """Generate a normal handwriting sample."""
    text = random.choice(WORDS + SENTENCES)
    img = render_text(text)

    # Apply mild distortions
    img = add_line_wobble(img)
    img = add_distortion(img)
    if random.random() > 0.5:
        img = vary_thickness(img)
    if random.random() > 0.7:
        img = add_noise(img, intensity=0.02)

    return img


def generate_reversal(idx):
    """Generate a handwriting sample with letter reversals."""
    text = random.choice(WORDS + SENTENCES)

    # Apply reversals to confusable letters
    reversed_text = ""
    has_reversal = False
    for ch in text:
        if ch.lower() in REVERSAL_MAP and random.random() > 0.3:
            reversed_text += REVERSAL_MAP[ch.lower()]
            has_reversal = True
        else:
            reversed_text += ch

    # If no reversal happened, force one
    if not has_reversal:
        reversed_text = list(reversed_text)
        for i, ch in enumerate(reversed_text):
            if ch.lower() in REVERSAL_MAP:
                reversed_text[i] = REVERSAL_MAP[ch.lower()]
                break
        reversed_text = "".join(reversed_text)

    img = render_text(reversed_text)

    # Also add some visual reversal artifacts
    if random.random() > 0.5:
        # Flip a portion of the image horizontally (simulating mirror writing)
        h, w = img.shape
        start_x = random.randint(0, w // 3)
        end_x = random.randint(w // 2, w)
        img[:, start_x:end_x] = np.fliplr(img[:, start_x:end_x])

    img = add_line_wobble(img)
    img = add_distortion(img)
    if random.random() > 0.3:
        img = vary_thickness(img)
    img = add_noise(img, intensity=0.03)

    return img


def generate_corrected(idx):
    """Generate a handwriting sample with corrections/strikethroughs."""
    text = random.choice(WORDS + SENTENCES)
    font_size = random.randint(28, 44)
    img = render_text(text, font_size=font_size)

    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)

    h, w = img.shape

    # Add strikethrough lines
    num_strikes = random.randint(1, 3)
    for _ in range(num_strikes):
        y = random.randint(h // 4, 3 * h // 4)
        x1 = random.randint(10, w // 3)
        x2 = random.randint(w // 2, w - 10)
        thickness = random.randint(2, 4)
        draw.line([(x1, y), (x2, y + random.randint(-5, 5))],
                  fill=random.randint(0, 30), width=thickness)

    # Add scribble-out circles/loops over parts
    if random.random() > 0.4:
        cx = random.randint(w // 4, 3 * w // 4)
        cy = random.randint(h // 4, 3 * h // 4)
        r = random.randint(15, 35)
        for _ in range(random.randint(2, 5)):
            offset = random.randint(-5, 5)
            draw.ellipse(
                [cx - r + offset, cy - r + offset, cx + r + offset, cy + r + offset],
                outline=random.randint(0, 40), width=2
            )

    # Write correction text above or below
    if random.random() > 0.3:
        correction_text = random.choice(WORDS)
        small_font = get_font(random.randint(22, 32))
        offset_x = random.randint(20, w // 2)
        offset_y = random.choice([
            random.randint(5, h // 4),
            random.randint(3 * h // 4, h - 20),
        ])
        draw.text((offset_x, offset_y), correction_text,
                  fill=random.randint(0, 50), font=small_font)

    img = np.array(pil_img)

    # Add more aggressive distortions
    img = add_line_wobble(img)
    img = add_distortion(img)
    img = vary_thickness(img)
    img = add_noise(img, intensity=0.04)

    return img


GENERATORS = {
    "Normal": generate_normal,
    "Reversal": generate_reversal,
    "Corrected": generate_corrected,
}


def main():
    print("Generating synthetic handwriting dataset...")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Samples per class: {SAMPLES_PER_CLASS}")
    print()

    for class_name in CLASSES:
        class_dir = os.path.join(OUTPUT_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)

        generator = GENERATORS[class_name]
        print(f"Generating {class_name}...")

        for i in range(SAMPLES_PER_CLASS):
            img = generator(i)
            filepath = os.path.join(class_dir, f"{class_name.lower()}_{i:04d}.png")
            cv2.imwrite(filepath, img)

            if (i + 1) % 500 == 0:
                print(f"  {i + 1}/{SAMPLES_PER_CLASS}")

        print(f"  Done: {SAMPLES_PER_CLASS} images saved to {class_dir}")

    print(f"\nDataset generation complete! Total: {SAMPLES_PER_CLASS * len(CLASSES)} images")


if __name__ == "__main__":
    main()
