from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "helloworld")

def ocr_with_ocr_space(file):
    url = "https://api.ocr.space/parse/image"
    payload = {
        "apikey": OCR_SPACE_API_KEY,
        "language": "spa",
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

def extract_features(full_text):
    lines = full_text.splitlines()
    characteristics = []

    # Buscar el índice donde empieza el bloque de características (línea con kg y rpm)
    start_index = -1
    for i, line in enumerate(lines):
        if re.search(r'\b\d+\s*kg\b', line.lower()) and re.search(r'\b\d{3,4}\s*rpm\b', line.lower()):
            start_index = i + 1  # Comenzamos desde la línea siguiente
            break

    if start_index == -1:
        return []  # No se encontró el punto de inicio

    # Agrupar líneas en características completas
    buffer = ''
    for line in lines[start_index:]:
        if not line.strip():
            continue  # Saltar líneas vacías

        if buffer:
            if line and line[0].islower():
                buffer += ' ' + line.strip()
            else:
                characteristics.append(buffer.strip())
                buffer = line.strip()
        else:
            buffer = line.strip()

        if len(characteristics) == 6:
            break

    if buffer and len(characteristics) < 6:
        characteristics.append(buffer.strip())

    return characteristics[:6]

@app.route('/ocr-header', methods=['POST'])
def ocr_header():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    full_text = ocr_with_ocr_space(file)
    first_line = full_text.strip().splitlines()[0] if full_text else ""

    text_lower = full_text.lower()
    hon_detected = "Sí" if "hon" in text_lower or "wifi" in text_lower else "No"
    wifi_detected = "WiFi" if "wifi" in text_lower else ""

    # Extraer características importantes
    features = extract_features(full_text)

    return jsonify({
        "header_text": first_line,
        "full_text": full_text,
        "hon_detected": hon_detected,
        "wifi_detected": wifi_detected,
        "features": features
    })

@app.route('/ping')
def ping():
    return "pong"
