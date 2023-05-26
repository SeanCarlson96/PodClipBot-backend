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

# @application.route('/api/fonts', methods=['GET'])
# def get_fonts():
#     fonts = TextClip.list('font')
#     return jsonify(fonts)