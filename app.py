from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "helloworld")  # valor por defecto

def ocr_with_ocr_space(file):
    url = "https://api.ocr.space/parse/image"
    payload = {
        "apikey": OCR_SPACE_API_KEY,
        "language": "eng",
        "isOverlayRequired": False,
        "scale": True,
        "OCREngine": 2
    }
    files = {"filename": (file.filename, file.stream, file.mimetype)}
    response = requests.post(url, data=payload, files=files)
    result = response.json()

    try:
        return result["ParsedResults"][0]["ParsedText"].strip()
    except Exception:
        return "Error: No se pudo leer texto"

@app.route('/ocr-header', methods=['POST'])
def ocr_header():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    full_text = ocr_with_ocr_space(file)
    first_line = full_text.strip().splitlines()[0] if full_text else ""

    # Detección de palabras clave (ignorando mayúsculas/minúsculas)
    text_lower = full_text.lower()
    hon_detected = "Sí" if ("hon" or "wifi") in text_lower else "no"
    wifi_detected = "WiFi" if ("hon" or "wifi") in text_lower else ""

    return jsonify({
        "header_text": first_line,
        "full_text": full_text,
        "hon_detected": hon_detected,
        "wifi_detected": wifi_detected
    })

@app.route('/ping')
def ping():
    return "pong"
