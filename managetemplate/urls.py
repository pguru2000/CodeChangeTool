from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='login'),

    path('convert_tool', views.convert_tool, name = 'convert_tool'),

    path('editrules', views.editrules, name = 'editrule'),
    path('newrule', views.newrule, name = 'rulelist'),
    path('loadrulelist', views.loadrulelist, name = 'loadrulelist'),
    path('uploadfiles', views.uploadfiles, name='uploadfiles'),
    path('startconvert', views.startconvert, name='startconvert'),
    path('startdownload', views.startdownload, name='startdownload'),
    path('deletefiles', views.deletefiles, name='deletefiles'),
    path('saveascsv', views.saveascsv, name='saveascsv'),

    path('deleteDuplicates', views.deleteDuplicates, name='deleteDuplicates'),
    

    path('viewconditions', views.viewconditions, name = 'viewconditions'),
    path('newcondition', views.newcondition, name = 'newcondition'),
    path('loadconditionlist', views.loadconditionlist, name = 'loadconditionlist'),
    path('addcondition', views.addcondition, name = 'addcondition'),

    path('create_condition', views.create_condition, name = 'create_condition'),
    path('edit_condition/<int:id>', views.edit_condition, name="edit_condition"),
    path('saveconditioncsv', views.saveconditioncsv, name="saveconditioncsv"),

    # path('create_project', views.create_project, name = 'create_project'),
    path('edit_project/<int:id>', views.edit_project, name="edit_project"),
    path('viewprojects', views.viewprojects, name='viewprojects'),
    path('newproject', views.newproject, name = 'projectlist'),
    path('loadprojectlist', views.loadprojectlist, name = 'loadprojectlist'),

    path('selectproject', views.selectproject, name="selectproject"),

    # variable condition
    path('viewvarconditions', views.viewvarconditions, name = 'viewvarconditions'),
    path('newvarcondition', views.newvarcondition, name = 'newvarcondition'),
    path('loadvarconditionlist', views.loadvarconditionlist, name = 'loadvarconditionlist'),
    path('addvarcondition', views.addvarcondition, name = 'addvarcondition'),

    path('create_varcondition', views.create_varcondition, name = 'create_varcondition'),
    path('edit_varcondition/<int:id>', views.edit_varcondition, name="edit_varcondition"),
    path('savevarconditioncsv', views.savevarconditioncsv, name="savevarconditioncsv"),

    # new permute function 2020.09.12
    # path('permutation', views.permutation, name = 'permutation'),
    # path('permutation_selectproject', views.permutation_selectproject, name = 'permutation_selectproject'),
    # path('permutation_viewprojects', views.permutation_viewprojects, name = 'permutation_viewprojects'),
    # path('loadpermutationprojectlist', views.loadpermutationprojectlist, name = 'loadpermutationprojectlist'),
    # path('newpermutationproject', views.newpermutationproject, name = 'newpermutationproject'),
    # path('edit_permutation_rules', views.edit_permutation_rules, name = 'edit_permutation_rules'),
    # path('uploadtxt', views.uploadtxt, name='uploadtxt'),
    # path('processtxt', views.processtxt, name='processtxt'),
    # path('update_permutation_rule', views.update_permutation_rule, name='update_permutation_rule'),
    # path('permutation_uploadfiles', views.permutation_uploadfiles, name='permutation_uploadfiles'),
    # path('permutation_startconvert', views.permutation_startconvert, name='permutation_startconvert'),
    # path('reset_template', views.reset_template, name='reset_template'),

    path('check_process', views.check_process, name='check_process'),

    path('cleanText', views.cleanText, name = 'cleanText'),
    path('uploadfiles_clean', views.uploadfiles_clean, name='uploadfiles_clean'),
    path('startconvert_clean', views.startconvert_clean, name='startconvert_clean'),


#    url(r'^login', views.login, name='login'),
#    url(r'^register', views.register, name='register'),
]
