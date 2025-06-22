from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.pos_scan, name='pos_scan'),
]
