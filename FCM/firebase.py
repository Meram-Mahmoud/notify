import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("C:\Users\Lenovo\FCM\notification-9d226-firebase-adminsdk-g4ow8-fdf72e5012.json")
firebase_admin.initialize_app(cred)