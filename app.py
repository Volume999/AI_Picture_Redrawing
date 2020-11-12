from flask import Flask, render_template, url_for, request, redirect
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

    def __repr__(self):
        return f'User {self.username}'


class Photobook(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    ownerId = db.Column(db.Integer, nullable=False)
    isPrivate = db.Column(db.Boolean, default=False)
    dateCreated = db.Column(db.Date)
    isDeleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'Photobook {self.name}'


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1000), nullable=False)
    photobookId = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Photo {self.name}'


class UserFollowsBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, nullable=False)
    photobookId = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'User {self.userId} follow {self.photobookId}'


@app.route('/', methods=['POST', 'GET'])
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


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        query = User.query.filter_by(username=username).filter_by(password=password).all()
        return 'Log-on' if len(query) != 0 else 'Incorrect credentials ' + username + ' ' + password
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name, pwd = request.form['username'], request.form['password']
        user = User(username=name, password=pwd)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)