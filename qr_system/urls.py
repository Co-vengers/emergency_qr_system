# qr_system/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/<str:qr_code_data>/', views.scan_qr, name='scan_qr'),
    path('profile/<str:qr_code_data>/', views.profile_view, name='profile_view'),
    path('register/', views.register, name='register'),
    path('register/<str:qr_code_data>/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('emergency-info/create/', views.create_emergency_info, name='create_emergency_info'),
    path('emergency-info/update/', views.update_emergency_info, name='update_emergency_info'),
    path('claim-qr-code/', views.claim_qr_code, name='claim_qr_code'),
    path('generate-qr-codes/', views.generate_qr_codes, name='generate_qr_codes'),
    
    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='qr_system/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

