from django.urls import path
from . import views

urlpatterns = [
    path('', views.GuestListView.as_view(), name='guest_list'),
    path('add/', views.add_guest, name='add_guest'),
    path('check/<int:pk>/', views.check_in_out, name='check_in_out'),
    path('update-companions/<int:pk>/', views.update_companions, name='update_companions'),
    path('toggle-check-in/<int:pk>/', views.toggle_check_in, name='toggle_check_in'),
    path('generate-confirmation-links/<int:pk>/', views.generate_confirmation_links, name='generate_confirmation_links'),
    path('confirm/<str:token>/', views.confirm_presence, name='confirm_presence'),
    path('confirmations/', views.guest_confirmation_dashboard, name='confirmation_dashboard'),
    path('confirmations/<int:pk>/', views.GuestConfirmationDetailView.as_view(), name='guest_confirmation_detail'),
]