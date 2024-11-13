from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home"),
    path('deeplearning/', views.deep_learning, name='deeplearning'),
    path('toggle_completed_status/', views.toggle_completed_status, name='toggle_completed_status'),

]