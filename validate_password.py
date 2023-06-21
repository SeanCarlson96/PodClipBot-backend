import re
from flask import jsonify

def validate_password(password):
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long."}), 400
    elif not re.search("[a-z]", password):
        return jsonify({"message": "Password must contain at least one lowercase letter."}), 400
    elif not re.search("[A-Z]", password):
        return jsonify({"message": "Password must contain at least one uppercase letter."}), 400
    elif not re.search("[0-9]", password):
        return jsonify({"message": "Password must contain at least one digit."}), 400
    elif not re.search("[~!@#$%^&*()_+\\-=\\[\\]{}|\\:;\"'<>,.?/]", password):
        return jsonify({"message": "Password must contain at least one special character."}), 400
    else:
        return True