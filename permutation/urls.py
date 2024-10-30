from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    # new permute function 2020.09.12
    path('new_permutation', views.new_permutation, name = 'new_permutation'),
    path('new_permutation_selectproject', views.new_permutation_selectproject, name = 'new_permutation_selectproject'),
    path('new_permutation_viewprojects', views.new_permutation_viewprojects, name = 'new_permutation_viewprojects'),
    path('new_loadpermutationprojectlist', views.new_loadpermutationprojectlist, name = 'new_loadpermutationprojectlist'),
    path('new_newpermutationproject', views.new_newpermutationproject, name = 'new_newpermutationproject'),
    path('new_edit_permutation_rules', views.new_edit_permutation_rules, name = 'new_edit_permutation_rules'),
    path('new_uploadtxt', views.new_uploadtxt, name='new_uploadtxt'),
    path('new_processtxt', views.new_processtxt, name='new_processtxt'),
    path('new_update_permutation_rule', views.new_update_permutation_rule, name='new_update_permutation_rule'),
    path('new_permutation_uploadfiles', views.new_permutation_uploadfiles, name='new_permutation_uploadfiles'),
    path('new_permutation_startconvert', views.new_permutation_startconvert, name='new_permutation_startconvert'),
    path('new_reset_template', views.new_reset_template, name='new_reset_template'),
]
