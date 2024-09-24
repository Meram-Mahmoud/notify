# utils.py

import requests
import json
from django.conf import settings

def send_fcm_notification(device_token, title, message):
    """
    Send a notification via Firebase Cloud Messaging (FCM).
    
    Args:
        device_token (str): The device token to send the notification to.
        title (str): The title of the notification.
        message (str): The message content of the notification.
    """
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + settings.FCM_SERVER_KEY, 
    }

    payload = {
        'to': device_token,
        'notification': {
            'title': title,
            'body': message,
            'sound': 'default',  # Optional sound for the notification
        },
        'data': {
            'title': title,
            'body': message,
        },
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()
