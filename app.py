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


def extract_features_after_ean_marker(text):
    lines = text.strip().splitlines()

    # 1. Buscar línea con EAN:
    ean_index = next((i for i, line in enumerate(lines) if 'EAN:' in line), None)
    if ean_index is None:
        return []

    # 2. Buscar línea con 'kg' o 'rpm' DESPUÉS de EAN
    start_index = None
    for i in range(ean_index + 1, len(lines)):
        line_lower = lines[i].lower()
        if "kg" in line_lower or "rpm" in line_lower:
            start_index = i + 1  # la siguiente línea marca el comienzo de features
            break

    if start_index is None or start_index >= len(lines):
        return []

    # 3. Recoger y unir características (hasta 6)
    features = []
    current = ""
    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped[0].islower() and current:
            current += " " + stripped
        else:
            if current:
                features.append(current.strip())
                if len(features) == 6:
                    break
            current = stripped

    if current and len(features) < 6:
        features.append(current.strip())

    return features


@app.route('/ocr-header', methods=['POST'])
def ocr_header():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    full_text = ocr_with_ocr_space(file)
    first_line = full_text.strip().splitlines()[0] if full_text else ""

    text_lower = full_text.lower()
    hon_detected = "Sí" if "hon" in text_lower or "wifi" in text_lower else "No"
    wifi_detected = "WiFi" if hon_detected == "Sí" else ""

    features = extract_features_after_ean_marker(full_text)

    response = {
        "header_text": first_line,
        "full_text": full_text,
        "hon_detected": hon_detected,
        "wifi_detected": wifi_detected,
    }

    # Agregar features individualmente
    for idx, feature in enumerate(features[:6], start=1):
        response[f"feature_{idx}"] = feature

    return jsonify(response)


@app.route('/ping')
def ping():
    return "pong"
