# import glob
import sys
from gevent import monkey
monkey.patch_all()

from http.client import BAD_REQUEST
# from json import dumps
# import pprint
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
from file_security_functions.safe_video_file import safe_video_file
# import httpx
import requests
import stripe
import tempfile
from email_validator import validate_email, EmailNotValidError
from validate_password import validate_password
from update_subscription import update_subscription

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

load_dotenv()

application = Flask(__name__)
CORS(application)
# CORS(application, resources={r"/*": {"origins": os.environ["FRONTEND_URL"]}})
# socketio = SocketIO(application, cors_allowed_origins=os.environ["FRONTEND_URL"])
socketio = SocketIO(application, cors_allowed_origins=os.environ["FRONTEND_URL"], async_mode='gevent')
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
application.config["MONGODB_SETTINGS"] = {
    'db': 'Cluster0',
    'host': os.environ["MONGODB_HOST"]
}
db = MongoEngine(application)
bcrypt = Bcrypt(application)
application.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(application)

# At the top of your script
# client_connected = False

# @socketio.on('connect')
# def connect():
#     global client_connected
#     client_connected = True
#     # print("Client connected")

# @socketio.on('disconnect')
# def disconnect():
#     global client_connected
#     client_connected = False
#     # print("Client disconnected")

@socketio.on('cancel_processing')
def handle_cancel_processing(data):
    clip_name = data['clipName']
    print(f"Canceling clip {clip_name}")
    socketio.emit('video_processing_progress', {'progress': 0})
    cancel_processing(clip_name, socketio)

import os
import tempfile

@application.route('/')
def hello_world():
    # print(sys.path)
    return 'Backend is running!'

@application.route('/test')
def test_1():
    return 'Test completed'

@application.route('/endpoint', methods=['POST'])
def handle_post():
    print("endpoint hit")
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'message': 'Bad request', 'success': False}), 400

    token = data['token']
    
    # Here, you can add code to do something with the token.
    # For example, you could verify it or store it.

    # After you're done processing, return a success message.
    return jsonify({'message': 'Request received successfully', 'success': token}), 200

@application.route('/trim', methods=['POST'])
def trim_video():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            print("Temporary directory path is:", tempdir)

            video_file = request.files.get('video-file')

            is_safe, message = safe_video_file(video_file, 8000)  # 500 is the maximum allowed file size in megabytes
            if not is_safe:
                return jsonify({'success': False, 'message': message})

            temp_file = os.path.join(tempdir, 'temp.mp4')
            video_file.save(temp_file)
            
            # Convert request.form into a regular dictionary, excluding start and end time data
            clip_info = {key: value for key, value in request.form.items() if not key.startswith(('start-time-', 'end-time-'))}

            music_file = request.files.get('music-file')
            if music_file:
                is_safe, message = safe_music_file(music_file, 200)
                if not is_safe:
                    return jsonify({'success': False, 'message': message})
                
                music_temp_file = os.path.join(tempdir, 'temp_music.mp3')
                music_file.save(music_temp_file)
                clip_info['music_file_path'] = music_temp_file


            watermark_file = request.files.get('watermark-file')
            if watermark_file:
                is_safe, message = safe_watermark_file(watermark_file, 20)
                if not is_safe:
                    return jsonify({'success': False, 'message': message})
                watermark_temp_file = os.path.join(tempdir, 'temp_watermark.png')
                watermark_file.save(watermark_temp_file)
                clip_info['watermark_file_path'] = watermark_temp_file

            # Get all keys in the form data that start with 'start-time-'
            start_time_keys = [key for key in request.form.keys() if key.startswith('start-time-')]

            # Loop over the start time keys and extract the corresponding start and end times
            for index, start_time_key in enumerate(start_time_keys):
                clip_number = start_time_key.split('-')[-1]
                start_time = request.form.get(start_time_key)
                end_time = request.form.get(f'end-time-{clip_number}')
                socketio.emit('build_action', {'action': 'Building'})

                build_clip(tempdir, temp_file, start_time, end_time, clip_number, socketio, clip_info)

            global clip_cancel_flags
            clip_cancel_flags.clear()
            return jsonify({'success': True, 'message': '/trim completed all clips'})

    except ValueError as e:
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
        tb = traceback.format

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
    
    validation_result = validate_password(data['password'])
    if validation_result is not True:
        return validation_result

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

# Configure Flask-Mail with Amazon SES
application.config['MAIL_SERVER'] = 'email-smtp.us-east-2.amazonaws.com'  # Replace with your Amazon SES server
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = os.environ["AWS_SES_SMTP_USERNAME"]  # Replace with your Amazon SES SMTP username
application.config['MAIL_PASSWORD'] = os.environ["AWS_SES_SMTP_PASSWORD"]  # Replace with your Amazon SES SMTP password
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
        sender='podclipbot@gmail.com', # Must be properly configured to send emails through a SMTP server
        recipients=[email]
    )
    msg.body = f'To reset your password, visit the following link: {reset_url}\n\nIf you did not request a password reset, please ignore this email.'
    mail.send(msg) # Commented out to prevent sending emails during development
    # print(msg.body)
    # print(reset_url)

    return jsonify({"message": "Password reset email sent"}), 200

@application.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    validation_result = validate_password(new_password)
    if validation_result is not True:
        return validation_result

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


        return jsonify({"message": "Password updated successfully. Redirecting to sign in page."}), 200

    except PyJWTError:
        return jsonify({"error": "Invalid or expired token"}), 401
    
VALID_SUBSCRIPTIONS = ['base', 'advanced', 'premium', 'none']

@application.route('/api/users/<string:user_id>', methods=['PATCH'])
def update_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if user is None:
            return jsonify({'message': 'User not found'}), 404

        if 'username' in request.json:
            username = request.json['username']
            # Validate username here
            if not username or not username.isalnum():
                return jsonify({'message': 'Invalid username. Username must contain only alphanumeric characters.'}), 400
            user.username = username
            # user.username = request.json['username']

        if 'email' in request.json:
            email = request.json['email']
            # Validate email here
            try:
                validate_email(email)
            except EmailNotValidError as e:
                return jsonify({"message": "Invalid email address. Please enter a valid email."}), 400
            existing_user = User.objects(email=email).first()
            if existing_user and str(existing_user.id) != user_id:
                return jsonify({"message": "Email address already in use. Please use a different email address."}), 400
            user.email = email
            # existing_user = User.objects(email=request.json['email']).first()
            # if existing_user and str(existing_user.id) != user_id:
            #     return jsonify({"message": "Email address already in use. Please use a different email address."}), 400
            # user.email = request.json['email']

        if 'subscription' in request.json:
            # Validate subscription here
            subscription = request.json['subscription']
            if subscription not in VALID_SUBSCRIPTIONS:
                return jsonify({'message': 'Invalid subscription. Subscription must be one of ' + ', '.join(VALID_SUBSCRIPTIONS)}), 400
            user.subscription = subscription
            # user.subscription = request.json['subscription']

        if 'defaultSettings' in request.json:
            # Validate defaultSettings here
            defaultSettings = request.json['defaultSettings']
            if not isinstance(defaultSettings, dict):
                return jsonify({'message': 'Invalid default settings. Default settings must be a dictionary.'}), 400
            user.defaultSettings = defaultSettings
            # user.defaultSettings = request.json['defaultSettings']

        user.save()

        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        # print(e)
        return jsonify({'message': 'An error occurred while updating user information.'}), 500

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

    validation_result = validate_password(new_password)
    if validation_result is not True:
        return validation_result
    
    # Update the password
    password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    User.objects(id=user_id).update_one(set__password_hash=password_hash)

    return jsonify({"message": "Password updated successfully"}), 200

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

@application.route('/verify-recaptcha', methods=['POST'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def verify_recaptcha():
    try:
        print("recaptcha hit")
        # print(request.headers)
        # print(request.data)
        data = request.get_json()
        token = data['token']

        # POST request to Google's reCAPTCHA API
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data = {
                'secret': os.environ["RECAPTCHA_SECRET_KEY"],
                'response': token,
            },
        )
        result = response.json()

        if result['success'] and result['score'] > 0.5:  # adjust the score limit as per your requirements
            # return jsonify({'status': 'failure', 'detail': 'Failed reCAPTCHA verification'}), 401 # for testing purposes
            return jsonify({'status': 'success', 'detail': 'User is likely human'}), 200
        else:
            print("no")
            return jsonify({'status': 'failure', 'detail': 'Failed reCAPTCHA verification'}), 401
    except Exception as e:
            print("An error occurred: ", str(e))
            traceback.print_exc(file=sys.stdout)
            return jsonify({'status': 'failure', 'detail': 'An error occurred: ' + str(e)}), 500

@application.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    print("checkout created")
    data = request.get_json()
    try:
        user_id = data['userId']
        priceId = data['priceId']
        
        stripe_price_id = priceId

        # Retrieve user with the specified id
        user = User.objects(id=user_id).first()

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        stripe_customer_id = user.stripe_customer_id

        if not stripe_customer_id:
            # Create new customer in Stripe
            customer = stripe.Customer.create(
                email=user.email
            )
            stripe_customer_id = customer['id']

            # Save the Stripe customer ID in the database
            # user.update(set__stripe_customer_id=stripe_customer_id)
            user.stripe_customer_id = stripe_customer_id
            user.save()

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=os.environ["FRONTEND_URL"] + '/returnedFromStripe/' + user_id,
            cancel_url=os.environ["FRONTEND_URL"] + '/subscriptions',
            client_reference_id=user_id,
            customer=stripe_customer_id,  # Pass the Stripe customer ID here
        )

        return jsonify({"sessionId": checkout_session['id']}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@application.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    socketio = SocketIO(application, cors_allowed_origins=os.environ["FRONTEND_URL"])
    print("webhook received")
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    socketio.emit('test_event', {'user_id': "test2", 'subscription': "tes2t"})
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET'))

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Fetch the subscription object using subscription id
            if 'subscription' in session:
                subscription_id = session['subscription']
                subscription = stripe.Subscription.retrieve(subscription_id)
                if 'items' in subscription and 'data' in subscription['items']:
                    price_id = subscription['items']['data'][0]['price']['id']
                    # Retrieve Stripe customer ID
                    stripe_customer_id = subscription['customer']
                    user_id = session['client_reference_id']
                    updated_subscription = update_subscription(session['client_reference_id'], price_id)
                    if not updated_subscription:
                        return jsonify({}), 200
                    else:
                        # print(client_connected)
                        # socketio.emit('subscription_updated', {'user_id': user_id, 'subscription': updated_subscription})
                        print("no longer need to emit")
                    
                    # Update user with Stripe customer ID
                    user = User.objects(id=user_id).first()
                    if user:
                        user.stripe_customer_id = stripe_customer_id
                        user.save()
                    else:
                        print('User not found: {user_id}')
                else:
                    print('Price ID not found in subscription')
            else:
                print('Subscription not found in session')

        elif event['type'] == 'customer.subscription.updated' or event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            user = User.objects(stripe_customer_id=subscription['customer']).first()
            if user is None:
                print('User not found')
                return jsonify({}), 400
            user_id = user.id
            # print(event)

            if event['type'] == 'customer.subscription.deleted' or subscription['status'] != 'active':
                price_id = 'none'
            else:
                price_id = subscription['items']['data'][0]['price']['id']

            updated_subscription = update_subscription(user_id, price_id)
            if not update_subscription(user_id, price_id):
                return jsonify({}), 200
            else:
                # print(client_connected)
                # socketio.emit('subscription_updated', {'user_id': user_id, 'subscription': updated_subscription})
                print("no longer need to emit")

    except ValueError as e:
        print(f'Invalid payload: {str(e)}')
        return jsonify({}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f'Invalid signature: {str(e)}')
        return jsonify({}), 400
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({}), 400
    socketio.emit('test_event', {'user_id': "test3", 'subscription': "test3"})
    return jsonify({}), 200

@application.route('/api/getUserById/<string:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = User.objects(id=user_id).first()
        if user is None:
            return jsonify({'message': 'User not found'}), 404

        # Build the user data dictionary
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "subscription": user.subscription,
            "defaultSettings": user.defaultSettings,
        }

        return jsonify({'user': user_data}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred while getting user information.'}), 500


# if __name__ == '__main__':  # commented out when using gunicorn
#     socketio.run(application, host='0.0.0.0', port=8000)
