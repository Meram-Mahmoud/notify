from django.urls import path
from .views import RegisterView, LoginView, LogoutView, SendNotificationView, NotificationListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send-notification/', SendNotificationView.as_view(), name='send_notification'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]
