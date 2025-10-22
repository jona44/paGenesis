from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
 
app_name = 'genesis'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('congregants/', views.congregant_list, name='congregant_list'),
    path('congregants/add/', views.add_congregant, name='add_congregant'),
    path('congregants/<int:pk>/', views.congregant_detail, name='congregant_detail'), 
    path('congregants/<int:pk>/edit/', views.congregant_edit, name='congregant_edit'), 
    path('congregants/<int:pk>/delete/', views.congregant_delete, name='congregant_delete'), 
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('record-contribution/', views.record_contribution, name='record_contribution'),
    path('contributions/', views.contribution_list, name='contributions_list'),
    path('congregant/<int:congregant_id>/contributions/', 
        views.get_congregant_contributions, name='congregant_contributions'),
    path('get-activity-details/', views.get_activity_details, name='get_activity_details'),
]