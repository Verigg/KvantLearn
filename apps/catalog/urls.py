from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.MaterialListView.as_view(), name='material_list'),
    path('<slug:slug>/', views.MaterialDetailView.as_view(), name='material_detail'),
    path('<slug:slug>/lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
]
