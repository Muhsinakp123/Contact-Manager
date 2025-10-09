from CM_app import views
from django.urls import  path

urlpatterns = [
    path('',views.login_View, name='login'),
    path('signup/',views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('User_dashboard/', views.User_dashboard, name='User_dashboard'),
    
    path('admin_users/',views.admin_users,name='admin_users'),
    path('admin_contacts/',views.admin_contacts,name='admin_contacts'),
    
    path('add_contact/', views.add_contact, name='add_contact'),
    path('update_contact/<int:id>/', views.update_contact, name='update_contact'),
    path('delete_contact/<int:id>/', views.delete_contact, name='delete_contact'),
]
    
