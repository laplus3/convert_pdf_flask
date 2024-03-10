from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import img2pdf

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    output_name = request.form.get('outputName', 'output')
    output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{output_name}.pdf')

    try:
        uploaded_files = request.files.getlist('images')

        if len(uploaded_files) == 0:
            return jsonify({'success': False, 'message': 'Please select a folder with images.'})

        image_paths = []

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_paths.append(file_path)

        with open(output_pdf_path, 'wb') as pdf_file:
            pdf_file.write(img2pdf.convert(image_paths))

        # Clean up uploaded image files
        for image_path in image_paths:
            os.remove(image_path)

        return send_file(output_pdf_path, as_attachment=True, download_name=f'{output_name}.pdf')
    except Exception as e:
        print('Error:', e)
        return jsonify({'success': False, 'message': 'Conversion failed.'})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)
