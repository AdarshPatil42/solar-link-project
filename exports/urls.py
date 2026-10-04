from django.urls import path
from . import views

app_name = 'exports'

urlpatterns = [
    path('', views.info_view, name='info'),
]
