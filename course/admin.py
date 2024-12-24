from django.contrib import admin
from course.models import User, RequestModel, Refund, ContactInfo, Complaint


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'phone', 'full_name', 'registration_date')
    list_filter = ('registration_date', 'user_id')
    search_fields = ('phone', 'full_name')
    ordering = ('registration_date', 'user_id')


@admin.register(RequestModel)
class RequestModelAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'department', 'request_type', 'status', 'details', 'created_at')
    list_filter = ('created_at', 'user_id')
    search_fields = ('department', 'request_type', 'status', 'details')
    ordering = ('created_at', 'user_id')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'surname', 'course', 'stream', 'reason', 'status', 'admin_notes')
    list_filter = ('status', 'user_id')
    search_fields = ('name', 'surname', 'course', 'stream', 'reason', 'admin_notes')
    ordering = ('user_id', 'name')


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'tg_username')
    list_filter = ('phone_number', 'tg_username')
    search_fields = ('phone_number', 'tg_username')
    ordering = ['-id']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user_id', "complain", "created_at")
    list_filter = ('created_at', 'user_id')
    search_fields = ('user_id', "complain")
    ordering = ['-id']