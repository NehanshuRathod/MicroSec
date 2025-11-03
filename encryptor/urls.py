from django.urls import path
from . import views

app_name = 'encryptor'  # helps Django differentiate URLs if you have multiple apps

urlpatterns = [
    path('', views.home, name='home'),
    path('encrypt/', views.encrypt_file, name='encrypt_file'),
    path('decrypt/', views.decrypt_file, name='decrypt_file'),
]
