from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username',
        'first_name', 'last_name',
        'password'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
