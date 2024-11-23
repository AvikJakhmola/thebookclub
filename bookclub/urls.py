from django.contrib import admin
from django.urls import path
from bookclub import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('unitview/<int:book_number>/', views.unitview, name='unitview'),
    path('toggle_page_completed_status/', views.toggle_page_completed_status, name='toggle_page_completed_status'),
    path('page/<str:page_id>/', views.page_detail, name='page_detail'),  # New route for page details
]

