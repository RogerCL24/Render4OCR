from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route('/ocr-header', methods=['POST'])
def ocr_header():
    file = request.files['file']
    if not file:
        return jsonify({"error": "No file provided"}), 400

    doc = fitz.open("pdf", file.read())
    page = doc[0]
    rect = fitz.Rect(30, 30, 200, 80)  # ajusta según posición del texto/logo
    pix = page.get_pixmap(clip=rect, dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    text = pytesseract.image_to_string(img, lang="eng")
    return jsonify({"header_text": text.strip()})
