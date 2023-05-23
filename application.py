import glob
from http.client import BAD_REQUEST
import pprint
import traceback
from flask import Flask, jsonify, request, send_from_directory, make_response, Response
from flask_cors import CORS
from auth_decorator import jwt_required
import time
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity
from jwt.exceptions import PyJWTError
from jwt import decode
from file_security_functions.safe_image_file import safe_watermark_file
from file_security_functions.safe_music_file import safe_music_file
from models import User
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO
import logging
from flask_mail import Mail, Message
import datetime
from functions.build_clip import build_clip, cancel_processing, clip_cancel_flags
from moviepy.editor import TextClip
from file_security_functions.safe_video_file import safe_video_file

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

load_dotenv()

application = Flask(__name__)
CORS(application)
# socketio = SocketIO(application, cors_allowed_origins="http://localhost:3000")
socketio = SocketIO(application, cors_allowed_origins=os.environ["FRONTEND_URL"])
application.config["MONGODB_SETTINGS"] = {
    'db': 'Cluster0',
    'host': os.environ["MONGODB_HOST"]
}
db = MongoEngine(application)
bcrypt = Bcrypt(application)
application.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(application)

@socketio.on('cancel_processing')
def handle_cancel_processing(data):
    clip_name = data['clipName']
    print(f"Canceling clip {clip_name}")
    socketio.emit('video_processing_progress', {'progress': 0})
    cancel_processing(clip_name, socketio)

@application.route('/trim', methods=['POST'])
def trim_video():
    temp_file = None
    try:
        video_file = request.files.get('video-file')

        is_safe, message = safe_video_file(video_file, 8000)  # 500 is the maximum allowed file size in megabytes
        if not is_safe:
            return jsonify({'success': False, 'message': message})

        temp_file = 'temp.mp4'
        video_file.save(temp_file)
        
        # Convert request.form into a regular dictionary, excluding start and end time data
        clip_info = {key: value for key, value in request.form.items() if not key.startswith(('start-time-', 'end-time-'))}


        music_file = request.files.get('music-file')
        if music_file:
            is_safe, message = safe_music_file(music_file, 200)
            if not is_safe:
                return jsonify({'success': False, 'message': message})
            
            music_temp_file = 'temp_music.mp3'
            music_file.save(music_temp_file)
            clip_info['music_file_path'] = music_temp_file


        watermark_file = request.files.get('watermark-file')
        if watermark_file:
            is_safe, message = safe_watermark_file(watermark_file, 20)
            if not is_safe:
                return jsonify({'success': False, 'message': message})
            watermark_temp_file = 'temp_watermark.png'
            watermark_file.save(watermark_temp_file)
            clip_info['watermark_file_path'] = watermark_temp_file

        # print(clip_info)

        # Get all keys in the form data that start with 'start-time-'
        start_time_keys = [key for key in request.form.keys() if key.startswith('start-time-')]

        # Loop over the start time keys and extract the corresponding start and end times
        for index, start_time_key in enumerate(start_time_keys):
            clip_number = start_time_key.split('-')[-1]
            start_time = request.form.get(start_time_key)
            end_time = request.form.get(f'end-time-{clip_number}')
            socketio.emit('build_action', {'action': 'Building'})

            build_clip(temp_file, start_time, end_time, clip_number, socketio, clip_info)

        global clip_cancel_flags
        clip_cancel_flags.clear()
        return jsonify({'success': True, 'message': '/trim completed all clips'})

    # except Exception as e:
    #     tb = traceback.format_exc()
    #     error_line = tb.split("\n")[-2]
    #     return jsonify({'success': False, 'message': f'Error: {str(e)}', 'detail': tb, 'error_line': error_line})
    
    # finally:
    except BAD_REQUEST as e:
        # This will catch errors related to the request data
        return jsonify({'success': False, 'Hmm, our bot did not like that request. Please try again.': str(e)}), 400
    except FileNotFoundError as e:
        # This will catch errors related to file not found
        return jsonify({'success': False, 'There was an issue finding one of the files you provided, please try again.': str(e)}), 404
    except PermissionError as e:
        # This will catch errors related to file permissions
        return jsonify({'success': False, 'We came across a 403 error with one of your files. Please try again.': str(e)}), 403
    except Exception as e:
        # This will catch all other types of exceptions
        tb = traceback.format_exc()
        error_line = tb.split("\n")[-2]
        return jsonify({'success': False, 'Sorry, something went wrong. Rest assured we are working on it. Please try again later.': f'Error: {str(e)}', 'detail': tb, 'error_line': error_line}), 500
    finally:
        # global clip_cancel_flags
        clip_cancel_flags.clear()
        temp_files = glob.glob('temp*') + glob.glob('SPEAKER*')
        for temp_file in temp_files:
            if os.path.isfile(temp_file):
                os.remove(temp_file)

@application.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    response = make_response(send_from_directory('uploads', filename))
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'video/mp4'
    response.headers['Cache-Control'] = 'no-store'  # Add this line
    return response

@application.route('/api/music_files', methods=['GET'])
def get_music_files():
    music_directory = 'music'
    music_files = os.listdir(music_directory)
    return jsonify(music_files)
@application.route('/api/music/<path:filename>', methods=['GET'])
def get_music_file(filename):
    return send_from_directory('music', filename)

@application.route('/progress')
def progress():
    def generate():
        for i in range(101):
            yield 'data: %d\n\n' % i
            time.sleep(0.1)  # simulate delay
    return Response(generate(), mimetype='text/event-stream')

@application.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    existing_user = User.objects(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email address already in use. Please use a different email address."}), 400

    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
                email=data['email'], 
                username=data['username'], 
                password_hash=password_hash, 
                subscription='none', 
                defaultSettings={
                    'subtitlesToggle': True,
                    'musicToggle': True,
                    'volume': 50,
                    'font': 'Arial',
                    'fontSize': 15,
                    'subtitleColor': '#ffffff',
                    'subtitleBackgroundToggle': False,
                    'musicChoice': 'random',
                    'watermarkToggle': True,
                    'subtitleBackgroundColor': '#000000',
                    'strokeWidth': 0,
                    'strokeColor': '#000000',
                    'subtitlePositionHorizontal': 'center',
                    'subtitlePositionVertical': 35,
                    'subtitleSegmentLength': 10,
                    'musicFadeToggle': True,
                    'diarizationToggle': False,
                    'secondSpeakerColor': "#FFFF00",
                    'thirdSpeakerColor': "#0000FF",
                    'fourthSpeakerColor': "#008000",
                    'fifthSpeakerColor': "#FF0000",
                    'musicDuration': 100,
                    'watermarkPositionHorizontal': "center",
                    'watermarkPositionVertical': 25,
                    'watermarkSize': 200,
                    'watermarkOpacity': 100,
                    'watermarkDuration': 100,
                }
                )
    # Wrap the save operation in a try/except block
    try:
        user.save()
    except Exception as e:
        return jsonify({"message": "Something went wrong while trying to register. Please try again later."}), 500


    return jsonify({"message": "User registered successfully."}), 201

# @application.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.objects.get(email=data['email'])
#     if user and bcrypt.check_password_hash(user.password_hash, data['password']):
#         access_token = create_access_token(identity=str(user.id))
#         user_data = {
#                         "id": str(user.id),
#                         "email": user.email,
#                         "username": user.username,
#                         "subscription": user.subscription,
#                         "defaultSettings": user.defaultSettings,
#                     }
#         return jsonify({"access_token": access_token, "user": user_data}), 200
#     else:
#         return jsonify({"message": "Invalid email or password."}), 401

@application.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        user = User.objects(email=data['email']).first()
        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=str(user.id))
            user_data = {
                            "id": str(user.id),
                            "email": user.email,
                            "username": user.username,
                            "subscription": user.subscription,
                            "defaultSettings": user.defaultSettings,
                        }
            return jsonify({"access_token": access_token, "user": user_data}), 200
        else:
            return jsonify({"message": "Invalid email or password."}), 401
    except (AttributeError, KeyError):
        return jsonify({"message": "Invalid request. Please provide email and password."}), 400
    except User.DoesNotExist:
        return jsonify({"message": "User with given email doesn't exist."}), 404
    except Exception as e:
        return jsonify({"message": f"An error occurred while logging in: {str(e)}"}), 500

@application.route('/protected', methods=['GET'])
@jwt_required
def protected_route():
    user_id = get_jwt_identity()
    user = User.objects.get(id=user_id)
    return jsonify({"message": f"Welcome, {user.username}!"})

# Configure Flask-Mail (use your own email settings)
application.config['MAIL_SERVER'] = 'smtp.gmail.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = 'carlsonseanr@example.com'
application.config['MAIL_PASSWORD'] = 'your-email-password'
mail = Mail(application)

@application.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    # Check if the email address already exists in the database
    user = User.objects(email=data['email']).first()
    if not user:
        return jsonify({"error": "Email not found"}), 404

    # Generate a reset token
    token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=1))

    # Send a password reset email
    # reset_url = f'http://localhost:3000/reset-password?token={token}'
    reset_url = f'{os.environ["FRONTEND_URL"]}/reset-password?token={token}'
    msg = Message(
        'Password Reset Request',
        sender='noreply@example.com',
        recipients=[email]
    )
    msg.body = f'To reset your password, visit the following link: {reset_url}\n\nIf you did not request a password reset, please ignore this email.'
    # mail.send(msg) -- Commented out to prevent sending emails during development
    print(msg.body)

    return jsonify({"message": "Password reset email sent"}), 200

@application.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Missing token or password"}), 400

    try:
        decoded_token = decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['sub']
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update the password
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        User.objects(id=user_id).update_one(set__password_hash=password_hash)


        return jsonify({"message": "Password updated successfully"}), 200

    except PyJWTError:
        return jsonify({"error": "Invalid or expired token"}), 401

# @application.route('/api/users/<string:user_id>', methods=['PATCH'])
# def update_user(user_id):
#     user = User.objects(id=user_id).first()
#     if user is None:
#         return jsonify({'message': 'User not found'}), 404
#     if 'username' in request.json:
#         user.username = request.json['username']
#     if 'email' in request.json:
#         user.email = request.json['email']
#     if 'subscription' in request.json:
#         user.subscription = request.json['subscription']
#     if 'defaultSettings' in request.json:
#         user.defaultSettings = request.json['defaultSettings']
#     user.save()
#     return jsonify({'message': 'User updated successfully'}), 200
@application.route('/api/users/<string:user_id>', methods=['PATCH'])
def update_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if user is None:
            return jsonify({'message': 'User not found'}), 404

        if 'username' in request.json:
            # TODO: Validate username here
            user.username = request.json['username']

        if 'email' in request.json:
            existing_user = User.objects(email=request.json['email']).first()
            if existing_user and str(existing_user.id) != user_id:
                return jsonify({"message": "Email address already in use. Please use a different email address."}), 400
            # TODO: Validate email here
            user.email = request.json['email']

        if 'subscription' in request.json:
            # TODO: Validate subscription here
            user.subscription = request.json['subscription']

        if 'defaultSettings' in request.json:
            # TODO: Validate defaultSettings here
            user.defaultSettings = request.json['defaultSettings']

        user.save()

        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        # TODO: Consider logging the exception here for debugging purposes
        return jsonify({'message': 'An error occurred while updating user information.'}), 500


# @application.route('/change-password', methods=['POST'])
# def change_password():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     old_password = data.get('old_password')
#     new_password = data.get('new_password')

#     if not user_id or not old_password or not new_password:
#         return jsonify({"error": "Missing user ID, old password or new password"}), 400

#     user = User.objects(id=user_id).first()

#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     # Check if the old password is correct
#     if not bcrypt.check_password_hash(user.password_hash, old_password):
#         return jsonify({"error": "Incorrect current password"}), 400

#     # Update the password
#     password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
#     User.objects(id=user_id).update_one(set__password_hash=password_hash)

#     return jsonify({"message": "Password updated successfully"}), 200
@application.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    user_id = data.get('user_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not user_id or not old_password or not new_password:
        return jsonify({"message": "Oops! Looks like you didn't provide all the necessary information. Please ensure that you've included your user ID, current password, and the new password."}), 400

    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({"message": "We're sorry, but we couldn't find a user with the provided ID. Please make sure you're logged in and try again."}), 404

    # Check if the old password is correct
    if not bcrypt.check_password_hash(user.password_hash, old_password):
        return jsonify({"message": "The current password you've entered seems to be incorrect. Please verify your password and try again."}), 400

    # Update the password
    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    User.objects(id=user_id).update_one(set__password_hash=password_hash)

    return jsonify({"message": "Password updated successfully"}), 200


# @application.route('/delete-account', methods=['DELETE'])
# def delete_account():
#     data = request.get_json()
#     user_id = data.get('user_id')

#     if not user_id:
#         return jsonify({"error": "Missing user ID"}), 400

#     user = User.objects(id=user_id).first()

#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     # Delete the user
#     user.delete()

#     return jsonify({"message": "Account deleted successfully"}), 200
@application.route('/delete-account', methods=['DELETE'])
def delete_account():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"message": "User ID is required to delete an account."}), 400

    user = User.objects(id=user_id).first()

    if not user:
        return jsonify({"message": "The account you're trying to delete does not exist. It might have been already deleted."}), 404

    # Delete the user
    user.delete()

    return jsonify({"message": "Your account has been deleted successfully."}), 200


# @application.route('/api/fonts', methods=['GET'])
# def get_fonts():
#     fonts = TextClip.list('font')
#     return jsonify(fonts)

# if __name__ == '__main__':
#     socketio.run(application)

socketio.run(application)