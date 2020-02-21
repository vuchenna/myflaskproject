from application import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(8), nullable=False)
    link = db.Column(db.String(1000), nullable=False, unique=True)

    def __repr__(self):
        return ''.join([
            'User ID: ', str(self.user_id), '\r\n',
            'Title: ', self.title, '\r\n', self.category, '\r\n', self.link
            ])


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    upload = db.relationship('Upload', backref='creator', lazy=True)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    def __repr__(self):
        return ''.join([
            'UserID: ', str(self.id), '\r\n',
            'Email: ', self.email, '\r\n'
            'Name: ', self.first_name, ' ', self.last_name
            ])

class SavedSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    song_id = db.Column(db.Integer)

