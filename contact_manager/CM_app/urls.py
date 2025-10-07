from CM_app import views
from django.urls import  path

urlpatterns = [
    path('',views.login_View, name='login'),
    path('signup/',views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('User-dashboard/', views.User_dashboard, name='User_dashboard'),
]