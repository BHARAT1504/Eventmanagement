from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    

    