from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
from resizeimage import resizeimage
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view_book')
def view_book():
    return render_template('view_book.html')

photos = UploadSet('photos', IMAGES)

UPLOAD_PHOTO_DEST = 'static/img'
app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_PHOTO_DEST
configure_uploads(app, photos)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        files = request.files.getlist("photo")
        filename = []
        for file in files:
            fn = photos.save(file)
            with open(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], fn), 'r+b') as f:
                img = Image.open(f)
                img = resizeimage.resize("thumbnail", img, [500, 500])
                img.save(UPLOAD_PHOTO_DEST + '/resized_' + fn, img.format)
            filename.append(fn)
        return ' '.join(filename)
    return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)