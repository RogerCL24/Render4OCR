from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OCR_SPACE_API_KEY = "helloworld"  # Cámbiala por tu clave real si la tienes

def ocr_with_ocr_space(file):
    url = "https://api.ocr.space/parse/image"
    payload = {
        "apikey": OCR_SPACE_API_KEY,
        "language": "eng",
        "isOverlayRequired": False,
        "scale": True,
        "OCREngine": 2  # Usa OCR Engine 2 (mejor que el 1)
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

    text = ocr_with_ocr_space(file)
    return jsonify({"header_text": text})
