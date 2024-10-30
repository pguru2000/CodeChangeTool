from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='login'),

    # variable condition

    path('viewclusterconditions', views.viewclusterconditions, name = 'viewclusterconditions'),
    path('newclustercondition', views.newclustercondition, name = 'newclustercondition'),
    path('loadclusterconditionlist', views.loadclusterconditionlist, name = 'loadclusterconditionlist'),
    path('addclustercondition', views.addclustercondition, name = 'addclustercondition'),

    path('create_clustercondition', views.create_clustercondition, name = 'create_clustercondition'),
    path('edit_clustercondition/<int:id>', views.edit_clustercondition, name="edit_clustercondition"),
    path('saveclusterconditioncsv', views.saveclusterconditioncsv, name="saveclusterconditioncsv"),
]
