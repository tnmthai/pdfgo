# app.py
from flask import Flask, request, send_file, render_template
from pypdf import PdfReader, PdfWriter
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('pdfs')
    writer = PdfWriter()
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    out_path = os.path.join(UPLOAD_FOLDER, "merged.pdf")
    with open(out_path, 'wb') as f:
        writer.write(f)
    return send_file(out_path, as_attachment=True)

import zipfile
import io

@app.route('/split', methods=['POST'])
def split():
    file = request.files['pdf']
    reader = PdfReader(file)
    output_paths = []
    
    # Create an in-memory zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_filename = f'page_{i+1}.pdf'
            output_path = os.path.join(UPLOAD_FOLDER, output_filename)
            with open(output_path, 'wb') as out:
                writer.write(out)
            output_paths.append(output_path)

            # Add to zip
            zipf.write(output_path, arcname=output_filename)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='split_pages.zip', mimetype='application/zip')
from pdf2image import convert_from_bytes

@app.route('/split-to-images', methods=['POST'])
def split_to_images():
    file = request.files['pdf']
    images = convert_from_bytes(file.read(), fmt='png')  # or 'jpeg'

    image_paths = []
    for i, img in enumerate(images):
        filename = f'page_{i+1}.png'
        path = os.path.join(UPLOAD_FOLDER, filename)
        img.save(path, 'PNG')  # or 'JPEG'
        image_paths.append(path)

    # Zip images and return
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for path in image_paths:
            zipf.write(path, arcname=os.path.basename(path))
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='pdf_pages.zip', mimetype='application/zip')

if __name__ == '__main__':
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
