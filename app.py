from flask import Flask, render_template, url_for, request, redirect, escape, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES
from PIL import Image
from resizeimage import resizeimage
import os
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = b'Alibek'

cards_per_page = 6


class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'User {self.username}'


class Photobook(db.Model):
    photobookId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photobookName = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    ownerId = db.Column(db.Integer, nullable=False)
    isPrivate = db.Column(db.Boolean, default=False)
    dateCreated = db.Column(db.Date, default=datetime.datetime.utcnow())
    isDeleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'Photobook {self.photobookName}'


class Photo(db.Model):
    photoId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photoName = db.Column(db.String(1000), nullable=False)
    photobookId = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Photo {self.photoName}'


class UserFollowsBooks(db.Model):
    ufbId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, nullable=False)
    photobookId = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'User {self.userId} follow {self.photobookId}'


def reinitialize(db):
    db.drop_all()
    db.create_all()
    us = User(username='admin', password='123')
    db.session.add(us)
    db.session.commit()


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/', methods=['POST', 'GET'])
def index():
    books = Photobook.query.limit(cards_per_page).all()
    def getFirstPhoto(photobookId):
        return Photo.query.join(Photobook, Photobook.photobookId == Photo.photobookId).filter(
        Photobook.photobookId == photobookId).first()
    firstPhoto = {b.photobookId: getFirstPhoto(b.photobookId).photoName if getFirstPhoto(b.photobookId) is not None else 'default.jpg' for b in books}
    print(firstPhoto)
    return render_template('index.html', books=books, firstPhoto=firstPhoto)


@app.route('/view_book/<int:id>')
def view_book(id):
    photos = Photo.query.filter_by(photobookId=id).limit(cards_per_page)
    photobook = Photobook.query.filter_by(photobookId=id).first()
    author = User.query.filter_by(userId=photobook.ownerId).first()
    return render_template('view_book.html', photos=photos, photobook=photobook, author=author)


photos = UploadSet('photos', IMAGES)

UPLOAD_PHOTO_DEST = 'static/img'
app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_PHOTO_DEST
configure_uploads(app, photos)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        photobook_name = request.form['book_name']
        desc = request.form['desc']
        # Photos
        files = request.files.getlist("photo")
        filename = []
        pb = Photobook(photobookName=photobook_name,
                       description=desc,
                       ownerId=session['id'])
        db.session.add(pb)
        db.session.commit()
        if any(f for f in files):
            for file in files:
                fn = photos.save(file)
                print(fn)
                filename.append(fn)
                photo = Photo(
                    photoName=fn, photobookId=pb.photobookId
                )
                db.session.add(photo)
        db.session.commit()
        flash('Your photobook has been added!')
        return redirect(url_for('index'))
        # return ' '.join([photobook_name, description, ' '.join(filename)])
    return render_template('upload.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        query = User.query.filter_by(username=username).filter_by(password=password).all()
        # return 'Log-on' if len(query) != 0 else 'Incorrect credentials ' + username + ' ' + password
        if len(query) == 1:
            session['username'] = username
            session['id'] = query[0].userId
            flash(f'Welcome, {username}')
            return redirect(url_for('index'))
        else:
            return 'There has been a problem with your login (incorrect credentials, broken database)'
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
