from django.contrib import admin
from django.urls import path
from bookclub import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('unitview/<int:book_number>/', views.unitview, name='unitview'),
    path('toggle_completed_status/', views.toggle_completed_status, name='toggle_completed_status'),
]
