from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models
from django.utils.translation import gettext as _


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {
            "fields": ('email', 'password'),
        }),
        (_('Personal Info'), {
            'fields': ('name', )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('last_login',)
        })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2')
        }),
    )
    search_fields = ('email',)


admin.register(models.Tag)
admin.register(models.Ingredient)
