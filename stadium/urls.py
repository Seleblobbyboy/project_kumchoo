from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
    path('schedule/', views.fields_schedule, name='fields_schedule'),
    path('bookings/', views.bookings_list, name='bookings_list'),
    path('bookings/update/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('matches/', views.matches_list, name='matches_list'),
    path('tournaments/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:tournament_id>/register-team/', views.register_team, name='register_team'),
    path('finances/', views.finances_list, name='finances_list'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('users/', views.user_management, name='user_management'),
]
