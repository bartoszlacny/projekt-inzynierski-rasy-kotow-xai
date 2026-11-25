import json
from pathlib import Path
import numpy as np
from PIL import Image
from tensorflow import keras

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "cat_breed_effnetV3_240.keras"
CLASSES_PATH = ROOT / "models" / "class_names.json"
DETECTOR_PATH = ROOT / "models" / "cat_detector.keras"
IMG_SIZE = (240, 240)
DETECTOR_SIZE = (224, 224)
CAT_THRESHOLD = 0.75

model = keras.models.load_model(MODEL_PATH, safe_mode=False)
detector = keras.models.load_model(DETECTOR_PATH)
class_names = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))

if model.output_shape[-1] != len(class_names):
    raise ValueError(
        f"Model ma {model.output_shape[-1]} wyjść, a lista klas {len(class_names)} elementów."
    )


def cat_score(image):
    img = image.resize(DETECTOR_SIZE)
    x = np.expand_dims(np.array(img, dtype="float32"), axis=0)
    return float(detector.predict(x, verbose=0)[0][0])


def is_cat(image):
    score = cat_score(image)
    return score >= CAT_THRESHOLD


def predict(image):
    img = image.resize(IMG_SIZE)
    x = np.expand_dims(np.array(img, dtype="float32"), axis=0)
    probs = model.predict(x, verbose=0)[0]
    top = np.argsort(probs)[::-1][:3]
    return [(class_names[i].replace("_", " "), float(probs[i])) for i in top]


_warmup_image = Image.new("RGB", IMG_SIZE)
predict(_warmup_image)
is_cat(_warmup_image)
