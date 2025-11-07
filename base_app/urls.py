from django.urls import path
from . import views

urlpatterns = [
    path('content-generator', views.query_view, name='Content Generator'),
]
