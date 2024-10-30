from django.http import HttpResponse,JsonResponse

import json
import threading
import time
import json

import datetime
from datetime import datetime as datetime_obj

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from utils import xlsmanager as xlsutil
from utils import zipmanager as ziputil
from utils import permutation_zipmanager as permutation_ziputil
from utils import permutation_txtmanager as txtutil

from utils.errorcode import ErrorCode as ec

from cluster.models import ClusterCondition as ClusterCondition

from managetemplate.models import VariableFields as VF

from os import listdir
from os.path import isfile, join
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring
from utils.download_root import get_download_root

from wsgiref.util import FileWrapper
from django.core import serializers

import json
import os
import csv
import urllib.request

#import pypdftk
#from .models import casetemplate

# Create your views here.

def convert_tool(request):

    return render(request, 'index.html')

def index(request):   

    return render(request, 'cluster_condition/viewclusterconditions.html')

def viewclusterconditions(request):
    return render(request, 'cluster_condition/viewclusterconditions.html')

def loadclusterconditionlist(request):
    project_name = request.COOKIES.get('project_name')
    data = ClusterCondition.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    cluster_clustercondition "
                          "WHERE "
                          "    project_name = '{}'".format(project_name)
                          )
    data_list = list(data)
    json_arr = []
    for item in data_list:
        id = item.id
        variable_name = item.variable_name
        condition_content = item.condition_content        
        text_for_fulfill = item.text_for_fulfill        
        text_for_not_fulfill = item.text_for_not_fulfill

        row = {
            "id": id,
            "Variable Name": variable_name,
            "Condition Content": condition_content,            
            "Text for fulfill": text_for_fulfill.replace("\n", "<br/>"),            
            "Text for not-fulfill": text_for_not_fulfill.replace("\n", "<br/>"),

        }
        json_arr.append(row)
    return JsonResponse({
        "data": json_arr
    })

def addclustercondition(request):
    variables = VF.objects.values_list("name").order_by("name")
    variables = list(variables)
    varis = []
    for i in range(len(variables)):
        varis.append(variables[i][0])
    return render(request, 'cluster_condition/addclustercondition.html', context={'variables': varis})

def create_clustercondition(request):
    variable_name = request.POST.get('Variable-Name')
    result = request.POST.get('result')
    project_name = request.COOKIES.get('project_name')
    
    cond_fulfill_txt = request.POST.get('cond_fulfill_txt')    
    cond_not_fulfill_txt = request.POST.get('cond_not_fulfill_txt')

    new_condition = ClusterCondition.objects.create(
        variable_name=variable_name,
        condition_content=result,        
        text_for_fulfill=cond_fulfill_txt,        
        text_for_not_fulfill=cond_not_fulfill_txt,
        project_name=project_name,
    )
    new_condition.save()
    return render(request, 'cluster_condition/viewclusterconditions.html')

def edit_clustercondition(request, id):
    result = ClusterCondition.objects.get(id=id)

    result.text_for_fulfill = repr(result.text_for_fulfill)
    result.text_for_not_fulfill = repr(result.text_for_not_fulfill)

    variables = VF.objects.values_list("name").order_by("name")
    variables = list(variables)
    varis = []
    for i in range(len(variables)):
        varis.append(variables[i][0])
    if request.method == "POST":

        result.variable_name = request.POST.get('Variable-Name')
        result.condition_content = request.POST.get('result')
        result.project_name = request.COOKIES.get('project_name')
        
        result.text_for_fulfill = request.POST.get('cond_fulfill_txt')        
        result.text_for_not_fulfill = request.POST.get('cond_not_fulfill_txt')
        result.save()
        print("go to viewcluster")

        return redirect('viewclusterconditions')
        
    return render(request, "cluster_condition/editclustercondition.html", context={"result": result, 'variables': varis })


def newclustercondition(request):
    project_name = request.COOKIES.get('project_name')

    # modified code
    from urllib import parse
    data_json = request.body
    data = parse.unquote_plus(data_json.decode('utf-8')).split('&')

    data_len = len(data)
    action = data[data_len - 1].split('=')[1]
    col_len = 5
    json_arr = []
    for i in range(data_len // col_len):

        if action == "remove":
            id = data[i*col_len].split('=')[1]

            delete = ClusterCondition.objects.get(id=id)
            json_arr.append({
                "id": delete.id,
                "Variable Name": delete.variable_name,
                "Condition Content": delete.condition_content,                
                "Text for fulfill": delete.text_for_fulfill.replace("\n", "<br/>"),                
                "Text for not-fulfill": delete.text_for_not_fulfill.replace("\n", "<br/>"),
            })
            delete.delete()
        elif action == "create":
            variable_name = data[i * col_len].split('=')[1]
            condition_content = data[i * col_len + 1].split('=')[1]            
            text_for_fulfill = data[i * col_len + 2].split('=')[1].replace('--\\--', '\n')            
            text_for_not_fulfill = data[i * col_len + 3].split('=')[1].replace('--\\--', '\n')

            template = ClusterCondition(variable_name=variable_name,
                    condition_content=condition_content,                    
                    text_for_fulfill=text_for_fulfill,                    
                    text_for_not_fulfill=text_for_not_fulfill,
                    project_name=project_name)
            template.save()
            id = template.id
            json_arr.append({
                "id": id,
                "Variable Name": variable_name,
                "Condition Content": condition_content,                
                "Text for fulfill": text_for_fulfill.replace('\n', '<br/>'),                
                "Text for not-fulfill": text_for_not_fulfill.replace('\n', '<br/>'),
            })

    return JsonResponse({
        "data": json_arr
    })


def saveclusterconditioncsv(request):
    project_name = request.COOKIES.get('project_name')
    data = ClusterCondition.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    cluster_clustercondition "
                          "WHERE "
                          "    project_name = '{}'".format(project_name)
                          )
    
    data_list = list(data)
    json_arr = []
    writer = csv.writer(open("static/csv/cluster_conditions.csv", 'w', newline='', encoding='utf-8'))
    # writer = csv.writer(open("static/csv/rules.csv", 'w', newline=''))
    writer.writerow(["Cluter Name", "Condition Content",  "Text for fulfill", "Text for not-fulfill"])
    for item in data_list:
        row = [item.variable_name, item.condition_content, item.text_for_fulfill.replace('\n', '--\\--'), item.text_for_not_fulfill.replace('\n', '--\\--')]
        writer.writerow(row)
    file_path = "static/csv/cluster_conditions.csv"

    if len(data_list) > 0:
        return JsonResponse({
            "success": 1,
            "download_csv": file_path
        })
    else:
        return JsonResponse({
            "success": 0
        })