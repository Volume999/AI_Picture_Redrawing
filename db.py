import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
