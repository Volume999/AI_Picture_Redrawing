from flask import Flask, render_template, url_for, request, redirect, escape, session, flash
from flask_uploads import UploadSet, configure_uploads, IMAGES
from db import db, User, Photo, Photobook, UserFollowsBooks, reinitialize

# initializing flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = b'Alibek'

#initialize db
db.init_app(app=app)

#For now, static pages
cards_per_page = 6


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/<index_filter>', methods=['POST', 'GET'])
def index(index_filter='public'):
    #filter depending on GET flag
    if index_filter == 'yourCollection':
        books = Photobook.query.filter_by(ownerId=session['id']).limit(cards_per_page).all()
    elif index_filter == 'following':
        books = Photobook.query \
            .join(UserFollowsBooks, Photobook.photobookId == UserFollowsBooks.photobookId). \
            filter(UserFollowsBooks.userId == session['id']).filter(Photobook.isPrivate == False).limit(
            cards_per_page).all()
    else:
        books = Photobook.query.filter_by(isPrivate=False).limit(cards_per_page).all()

    def getFirstPhoto(photobookId):
        # database query
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

#uploading photos
photos = UploadSet('photos', IMAGES)

UPLOAD_PHOTO_DEST = 'static/img'
app.config['UPLOADED_PHOTOS_DEST'] = UPLOAD_PHOTO_DEST
configure_uploads(app, photos)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Creating a photobook
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
    #Login page
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
        flash('Registration successful, please log in')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/delete/<int:id>')
def delete(id):
    #Deleting photobook
    # photobook
    pb = Photobook.query.filter_by(photobookId=id).first()
    db.session.delete(pb)
    # photos
    ps = Photo.query.filter_by(photobookId=id).all()
    for p in ps:
        db.session.delete(p)
    # follows
    ufp = UserFollowsBooks.query.filter_by(photobookId=id).all()
    for u in ufp:
        db.session.delete(u)
    # commit
    db.session.commit()
    flash('Photobook has been deleted!')
    return redirect(url_for('index'))


@app.route('/follow/<int:id>')
def follow(id):
    #Following photobooks
    ufb = UserFollowsBooks(userId=session['id'], photobookId=id)
    db.session.add(ufb)
    db.session.commit()
    flash('Successfully followed a book')
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    #Editing photobooks
    photobook = Photobook.query.filter_by(photobookId=id).first()
    if request.method == 'POST':
        name = request.form['book_name']
        isPrivate = request.form['isPrivate']
        desc = request.form['desc']
        photobook.photobookName = name
        photobook.isPrivate = isPrivate == 'private'
        photobook.description = desc
        db.session.commit()
        flash('photobook Updated successfully!')
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', photobook=photobook)


@app.route('/view_photo/<int:id>')
def view_photo(id):
    #View photo tab
    photo = Photo.query.filter_by(photoId=id).first()
    return render_template('view_photo.html', photo=photo)


if __name__ == "__main__":
    app.run(debug=True)
