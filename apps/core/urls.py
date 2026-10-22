from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('settings/', views.SiteSettingsEditView.as_view(), name='settings'),
    path('settings/users/', views.UsersListView.as_view(), name='users_list'),
    path('settings/users/<int:pk>/action/', views.UserActionView.as_view(), name='user_action'),
]
