from django.contrib import admin
from django.urls import path
from bookclub import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signup, name='signup'),  # Default route points to the signup page
    path('home/', views.home, name='home'),  # Route for the home page
    path('signup/', views.signup, name='signup'),  # Separate route for signup (optional)
    path('login/', views.login, name='login'),
    path('unitview/<int:book_number>/', views.unitview, name='unitview'),
    path('toggle_page_completed_status/', views.toggle_page_completed_status, name='toggle_page_completed_status'),
    path('update_user_progress/', views.update_user_progress, name='update_user_progress'),
    path('get_book_progress/<int:book_number>/', views.get_book_progress, name='get_book_progress'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
