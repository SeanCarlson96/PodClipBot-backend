from flask_mongoengine import Document
from mongoengine import StringField, DictField

class User(Document):
    email = StringField(required=True, unique=True)
    username = StringField(required=True)
    password_hash = StringField(required=True)
    subscription = StringField(required=True)
    defaultSettings = DictField()
