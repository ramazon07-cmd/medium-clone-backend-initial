from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Recommendation

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'birth_year', 'middle_name', 'avatar')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

admin.site.register(Recommendation)
