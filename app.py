import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

from helpers import analyze_image_with_yolo, analyze_video_with_yolo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}

def is_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in VIDEO_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Dosya seçilmedi!')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Dosya seçilmedi!')
            return redirect(request.url)

        if is_video_file(file.filename):
            # --- VİDEO İŞLEME ---
            results, video_filename = analyze_video_with_yolo(file)
            if results is not None:
                return render_template('video_result.html', results=results, video_file=video_filename)
            else:
                flash('Video analizi sırasında bir hata oluştu.')
                return redirect(request.url)
        else:
            # --- RESİM İŞLEME ---
            detections, image_filename = analyze_image_with_yolo(file)
            if detections is not None:
                return render_template('result.html', detections=detections, image_file=image_filename)
            else:
                flash('İzin verilmeyen dosya türü veya resim analizi sırasında hata oluştu.')
                return redirect(request.url)

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True) # İndirme için

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(port=1071, debug=True)