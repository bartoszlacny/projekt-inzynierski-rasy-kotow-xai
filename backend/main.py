import base64
import io
import logging
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from .model_service import is_cat, predict as predict_breed
from .xai.gradcam import gradcam
from .xai.lime_explainer import lime

MAX_SIZE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_FORMATS = {"JPEG", "PNG","WEBP", "BMP"}

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
app = FastAPI()
logger = logging.getLogger(__name__)

def image_to_data_url(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return "data:image/png;base64," + encoded


@app.post("/predict")
def predict(image: UploadFile = File(...)):

    data = image.file.read(MAX_SIZE_BYTES + 1)
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"Plik jest większy niż {MAX_SIZE_BYTES // (1024 * 1024)} MB.")

    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail="Nieobsługiwany format zdjęcia. Dozwolone formaty: JPG, PNG, WEBP, BMP."
                )

            pil_image = img.convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Nieobsługiwany format pliku. Dozwolone formaty: JPG, PNG, WEBP, BMP."
        )

    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=400,
            detail="Obraz ma zbyt dużą rozdzielczość."
        )

    except OSError:
        raise HTTPException(
            status_code=400,
            detail="Nie udało się odczytać obrazu. Plik może być uszkodzony."
        )

    finally:
        image.file.close()

    if not is_cat(pil_image):
        raise HTTPException(
            status_code=422,
            detail="Zdjęcie jest niewystarczająco wyraźne lub nie znajduje się na nim kot. \nZobacz jak powinno wyglądać zdjęcie na podstronie Instrukcja obsługi."
            )

    try:
        top3 = predict_breed(pil_image)
        gradcam_image = gradcam(pil_image)
        lime_image = lime(pil_image)

    except Exception:
        logger.exception("Błąd podczas analizy obrazu")
        raise HTTPException(
            status_code=500,
            detail="Błąd podczas analizy obrazu"
        )

    return {
        "top3": [{
                "breed_result": breed,
                "probability": float(probability)
            }
            for breed, probability in top3
        ],
        "gradcam": image_to_data_url(gradcam_image),
        "lime": image_to_data_url(lime_image),
    }


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")