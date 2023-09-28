from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active']
    list_display_links = ['username', 'email']
    list_editable = ['is_active']
    list_per_page = 10
    fieldsets = [
        [
            None,
            {'fields': ['email', 'password']},
        ],
        [
            _("Personal info"),
            {'fields': ['username', 'first_name', 'last_name']}
        ],
        [
            _('Permissions'),
            {
                'fields': [
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions'
                ]
            }
        ],
        [
            _('Dates'),
            {'fields': ['last_login', 'date_joined']}
        ]
    ]
    add_fieldsets = (
        (
            None,
            {
                'fields': [
                    'email', 'username', 'first_name', 'last_name',
                    'password1', 'password2'
                ],
            },
        ),
    )
