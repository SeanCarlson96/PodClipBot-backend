import os

from flask import jsonify

from models import User

def update_subscription(user_id, price_id):
    """ Update the subscription status based on the Stripe price ID """
    if price_id == os.environ.get('STRIPE_PRICE_ID_BASE'):
        new_status = 'base'
    elif price_id == os.environ.get('STRIPE_PRICE_ID_ADVANCED'):
        new_status = 'advanced'
    elif price_id == os.environ.get('STRIPE_PRICE_ID_PREMIUM'):
        new_status = 'premium'
    elif price_id == 'none':
        new_status = 'none'
    else:
        print(f'Unknown price ID: {price_id}')
        return False
    
    # Retrieve user with the specified id
    user = User.objects(id=user_id).first()
    if user is None:
        print('User not found')
        return jsonify({}), 400

    # Update the subscription status and save the changes
    # user.update(set__subscription=new_status)
    user.subscription = new_status
    user.save()
    
    return new_status