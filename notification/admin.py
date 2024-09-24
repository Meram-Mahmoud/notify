from django.contrib import admin

from django.contrib import admin
from .models import Notification, DeviceToken

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'message', 'created_at', 'read')
    search_fields = ('title', 'message', 'user__username')  # Search by title, message, and username
    list_filter = ('read', 'created_at')  # Filter by read status and creation date
    ordering = ('-created_at',)  # Order notifications by the most recent first

# Define the admin interface for the DeviceToken model
@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')  # Search by username and token
    ordering = ('-created_at',)  # Order tokens by the most recent first
