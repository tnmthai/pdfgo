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

@app.route('/split', methods=['POST'])
def split():
    file = request.files['pdf']
    reader = PdfReader(file)
    files = []
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        output = os.path.join(UPLOAD_FOLDER, f'page_{i+1}.pdf')
        with open(output, 'wb') as f:
            writer.write(f)
        files.append(output)
    # Optionally: zip the files and send
    return send_file(files[0], as_attachment=True)

if __name__ == '__main__':
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
