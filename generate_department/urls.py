from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('uploadfiles', views.uploadfiles, name = 'uploadfiles'),
    path('startconvert', views.startconvert, name = 'startconvert'),
    path('deletefiles', views.deletefiles, name = 'deletefiles'),
]
