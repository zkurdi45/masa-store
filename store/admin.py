from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser 
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'name', 'role', 'is_staff', 'is_active']
    search_fields = ['email', 'name']
    ordering = ['email']
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('name', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('name', 'role')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

from .models import Product, Basket, BasketItem
admin.site.register(Product)
admin.site.register(Basket)
admin.site.register(BasketItem)
