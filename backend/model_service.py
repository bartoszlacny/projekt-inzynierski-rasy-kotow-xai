import json
from pathlib import Path

import numpy as np
from PIL import Image
from tensorflow import keras

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "cat_breed_effnetV3_240.keras"
CLASSES_PATH = ROOT / "models" / "class_names.json"
IMG_SIZE = (240, 240)


model = keras.models.load_model(
    MODEL_PATH,
    safe_mode=False
)
class_names = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))

if model.output_shape[-1] != len(class_names):
    raise ValueError(
        f"Model ma {model.output_shape[-1]} wyjść, a lista klas {len(class_names)} elementów."
    )


def predict(image):
    img = image.resize(IMG_SIZE)
    x = np.expand_dims(np.array(img, dtype="float32"), axis=0)
    probs = model.predict(x, verbose=0)[0]
    top = np.argsort(probs)[::-1][:3]
    return [(class_names[i].replace("_", " "), float(probs[i])) for i in top]


def gradcam(image):
    return image


def lime(image):
    return image

_warmup_image = Image.new("RGB", IMG_SIZE)
predict(_warmup_image)