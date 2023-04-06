from flask_mongoengine import Document
from mongoengine import StringField

class User(Document):
    email = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
