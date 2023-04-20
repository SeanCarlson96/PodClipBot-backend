from flask import Flask, jsonify, request, send_from_directory, make_response, Response
from flask_cors import CORS
from auth_decorator import jwt_required
from edit_video import edit_video
import time
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity
from models import User
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv

load_dotenv()
print("MONGODB_HOST:", os.environ["MONGODB_HOST"])


app = Flask(__name__)
CORS(app)
app.config["MONGODB_SETTINGS"] = {
    'db': 'Cluster0',
    'host': os.environ["MONGODB_HOST"]
}
db = MongoEngine(app)
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)

@app.route('/trim', methods=['POST'])
def trim_video():
    video_file = request.files.get('video-file')
    start_time = float(request.form.get('start-time'))
    end_time = float(request.form.get('end-time'))
    output_filename = edit_video(video_file, start_time, end_time)
    return jsonify({'success': True, 'file': output_filename})


@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    response = make_response(send_from_directory('uploads', filename))
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'video/mp4'
    return response

@app.route('/progress')
def progress():
    def generate():
        for i in range(101):
            yield 'data: %d\n\n' % i
            time.sleep(0.1)  # simulate delay
    return Response(generate(), mimetype='text/event-stream')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(email=data['email'], username=data['username'], password_hash=password_hash, subscription='none')
    user.save()
    return jsonify({"message": "User registered successfully."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.objects.get(email=data['email'])
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "username": user.username,
                        "subscription": user.subscription,
                    }
        return jsonify({"access_token": access_token, "user": user_data}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

@app.route('/protected', methods=['GET'])
@jwt_required
def protected_route():
    user_id = get_jwt_identity()
    user = User.objects.get(id=user_id)
    return jsonify({"message": f"Welcome, {user.username}!"})


if __name__ == '__main__':
    app.run()