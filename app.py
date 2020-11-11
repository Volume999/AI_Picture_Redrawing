from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
from resizeimage import resizeimage
import os
import Database


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)


class Photobook(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    ownerId = db.Column(db.Integer, nullable=False)
    isPrivate = db.Column(db.Boolean, default=False)
    dateCreated = db.Column(db.Date)
    isDeleted = db.Column(db.Boolean, default=False)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1000), nullable=False)
    photobookId = db.Column(db.Integer, nullable=False)


class UserFollowsBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, nullable=False)
    photobookId = db.Column(db.Integer, nullable=False)


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
    if request.method == 'POST':
        photobook_name = request.form['book_name']
        description = request.form['desc']
        # Photos
        files = request.files.getlist("photo")
        filename = []
        for file in files:
            fn = photos.save(file)
            filename.append(fn)
        return ' '.join([photobook_name, description, ' '.join(filename)])
    return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)