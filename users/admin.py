from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Recommendation, Pin, Notification

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'birth_year', 'middle_name', 'avatar')
#     search_fields = ('username', 'first_name', 'last_name', 'email')
#     ordering = ('username',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'middle_name')
    list_display_links = ('id', 'username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'middle_name')
    list_filter = ('last_login', 'date_joined', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'middle_name', 'email', 'avatar', 'birth_year')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Recommendation)
admin.site.register(Pin)
admin.site.register(Notification)
