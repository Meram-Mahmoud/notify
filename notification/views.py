from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from firebase_admin import messaging
from .models import Notification, DeviceToken
from .serializers import NotificationSerializer, DeviceTokenSerializer
from rest_framework.permissions import AllowAny
from django.db import IntegrityError



class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow any user to register

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        device_token = request.data.get('device_token')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create user
            user = User.objects.create_user(username=username, password=password, email=email)

            # Save the device token if provided
            if device_token:
                DeviceToken.objects.create(user=user, token=device_token)

            # Send Welcome Notification
            title = "Welcome!"
            message_body = f"Thank you for registering, {username}!"
            send_fcm_notification(device_token, title, message_body)

            # Store notification in the database
            Notification.objects.create(user=user, title=title, message=message_body)

            return Response({'message': 'User registered and notified successfully'}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user to log in

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            # Send Login Notification
            device_token = DeviceToken.objects.filter(user=user).first()
            if device_token:
                title = "Login Successful"
                message_body = "You have successfully logged in."
                send_fcm_notification(device_token.token, title, message_body)
                Notification.objects.create(user=user, title=title, message=message_body)

            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can log out

    def post(self, request):
        try:
            request.user.auth_token.delete()

            # Send Logout Notification
            device_token = DeviceToken.objects.filter(user=request.user).first()
            if device_token:
                title = "Logout Successful"
                message_body = "You have successfully logged out."
                send_fcm_notification(device_token.token, title, message_body)
                Notification.objects.create(user=request.user, title=title, message=message_body)

            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'error': 'User is not logged in'}, status=status.HTTP_400_BAD_REQUEST)

# Custom Send Notification View
class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can send notifications

    def post(self, request):
        title = request.data.get('title')
        message_body = request.data.get('message')
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            device_token = DeviceToken.objects.filter(user=user).first()

            if device_token:
                send_fcm_notification(device_token.token, title, message_body)
                Notification.objects.create(user=user, title=title, message=message_body)
                return Response({'message': 'Notification sent'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User has no registered device token'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Fetch Notifications View
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication for accessing notifications

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        notification_id = request.data.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

# Utility to send Firebase notifications
def send_fcm_notification(device_token, title, message_body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message_body,
            ),
            token=device_token,
        )
        messaging.send(message)
    except Exception as e:
        print(f"Failed to send notification: {e}")
