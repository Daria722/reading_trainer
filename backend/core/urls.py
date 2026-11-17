from django.urls import path
from . import views

urlpatterns = [
    path('', views.text_list, name='text_list'),
    path('text/<int:pk>/read/', views.text_read, name='text_read'),
    path('text/<int:pk>/test/', views.text_test, name='text_test'),
    path('result/<int:pk>/', views.result, name='result'),
]