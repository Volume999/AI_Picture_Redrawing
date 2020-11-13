from flask import Flask, render_template, url_for, request, redirect, escape, session, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES
from db import db, User, Photo, Photobook, UserFollowsBooks, reinitialize

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = b'Alibek'

db.init_app(app=app)

cards_per_page = 6


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/', methods=['POST', 'GET'])
def index():
    books = Photobook.query.filter_by(isPrivate=False).limit(cards_per_page).all()

    def getFirstPhoto(photobookId):
        return Photo.query.join(Photobook, Photobook.photobookId == Photo.photobookId).filter(
            Photobook.photobookId == photobookId).first()

    firstPhoto = {b.photobookId: getFirstPhoto(b.photobookId).photoName if getFirstPhoto(
        b.photobookId) is not None else 'default.jpg' for b in books}
    return render_template('index.html', books=books, firstPhoto=firstPhoto)


@app.route('/view_book/<int:id>')
def view_book(id):
    photos = Photo.query.filter_by(photobookId=id).limit(cards_per_page).all()
    photobook = Photobook.query.filter_by(photobookId=id).first()
    author = User.query.filter_by(userId=photobook.ownerId).first()
    print(photos, photobook, author)
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
        isPrivate = request.form['isPrivate'] == 'private'
        # Photos
        files = request.files.getlist("photo")
        filenames = []
        pb = Photobook(photobookName=photobook_name,
                       description=desc,
                       ownerId=session['id'],
                       isPrivate=isPrivate)
        db.session.add(pb)
        db.session.commit()
        badext = False
        if any(f for f in files):
            for file in files:
                filename = file.filename
                if filename.split('.')[-1] not in ('png', 'jpg', 'jpeg'):
                    badext = True
                else:
                    fn = photos.save(file)
                    filenames.append(fn)
                    photo = Photo(
                        photoName=fn, photobookId=pb.photobookId
                    )
                    db.session.add(photo)
        db.session.commit()
        flash('Your photobook has been added!')
        if badext:
            flash('Some of your photos have not been added!')
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


@app.route('/delete/<int:id>')
def delete(id):
    pb = Photobook.query.filter_by(photobookId=id).first()
    db.session.delete(pb)
    db.session.commit()
    flash('Photobook has been deleted!')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
