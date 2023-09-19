#!/usr/bin/env python3

# import dependencies
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import os

# Connect to the database via flask-sqlalchemy
app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_STRING", 'postgresql://postgres:penis69@localhost:5432/streamingdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # to suppress a warning message
db = SQLAlchemy(app)

# ---------------------
# LINKING TABLES
# ---------------------
moive_link = db.Table('movie_link', 
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
    )

show_link = db.Table('show_link',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
    db.Column('show_id', db.Integer, db.ForeignKey('show.id'))
    )

# ---------------------
# CLASSES
# ---------------------
class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1500))
    shortDescription = db.Column(db.String(100))
    length = db.Column(db.Integer)
    year = db.Column(db.Integer)
    language = db.Column(db.String(3))
    score = db.Column(db.String(10))
    ageRec = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    service = db.Column(db.String(50))
    link = db.Column(db.String(300))
    image = db.Column(db.String(200))

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(1500))
    shortDescription = db.Column(db.String(100))
    score = db.Column(db.String(10))
    episodes = db.Column(db.Integer)
    seasons = db.Column(db.Integer)
    episodeLength = db.Column(db.Integer)
    year = db.Column(db.Integer)
    language = db.Column(db.String(4))
    lastYear = db.Column(db.String(4))
    ageRec = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    service = db.Column(db.String(50))
    link = db.Column(db.String(300))
    image = db.Column(db.String(200))

class Actor(db.Model):
    __tablename__ = 'actor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date)
    birthPlace = db.Column(db.String(250))
    gender = db.Column(db.String(10))
    bio = db.Column(db.String(7000))
    shortBio = db.Column(db.String(100))
    image = db.Column(db.String(200))

    movies = db.relationship('Movie', secondary='movie_link', backref='acts')
    shows = db.relationship('Show', secondary='show_link', backref='acts')

db.create_all()