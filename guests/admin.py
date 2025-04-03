from django.contrib import admin
from .models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'companions', 'checked_in', 'companions_checked_in')
    list_filter = ('checked_in',)
    search_fields = ('name', 'code')
    ordering = ('name',)