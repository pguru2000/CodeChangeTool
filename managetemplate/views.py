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
from os import listdir
from os.path import isfile, join
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring
from utils.download_root import get_download_root
from managetemplate.models import ConversionRule as CR
from managetemplate.models import Condition as CD
from managetemplate.models import VariableFields as VF
from managetemplate.models import Projects as PJ
from managetemplate.models import Projects as PJ
from managetemplate.models import VariableCondition as VARCD
from managetemplate.models import PermutationProjects
from managetemplate.models import PermutationGeneral
from managetemplate.models import PermutationParagraphs
from wsgiref.util import FileWrapper
from django.core import serializers

import json
import os
import csv
import urllib.request
from .models import ConversionRule


#import pypdftk
#from .models import casetemplate

# Create your views here.

def convert_tool(request):

    return render(request, 'index.html')

def index(request):
    project_list = PJ.objects.values_list("name")

    data = PJ.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    managetemplate_projects "
                          "ORDER BY "
                          "    name "
                          )
    data_list = list(data)

    arr = []
    for item in data_list:
        arr.append(item.name)

    return render(request, 'selectproject.html', context={'name_list': arr})


def editrules(request):
    return render(request, 'editrule.html')

def viewconditions(request):
    return render(request, 'viewconditions.html')

def selectproject(request):
    project_list = PJ.objects.values_list("name")

    data = PJ.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    managetemplate_projects "
                          "ORDER BY "
                          "    name "
                          )
    data_list = list(data)

    arr = []
    for item in data_list:
        arr.append(item.name)

    return render(request, 'selectproject.html', context={'name_list': arr})

def addcondition(request):
    variables = VF.objects.values_list("name").order_by("name")
    variables = list(variables)
    varis = []
    for i in range(len(variables)):
        varis.append(variables[i][0])
    return render(request, 'addcondition.html', context={'variables': varis})

def edit_condition(request, id):
    result = CD.objects.get(id=id)
    variables = VF.objects.values_list("name").order_by("name")
    variables = list(variables)
    varis = []
    for i in range(len(variables)):
        varis.append(variables[i][0])
    if request.method == "POST":
        result.condition_id = request.POST.get('name')
        result.condition_content = request.POST.get('result')
        result.save()
        return redirect("viewconditions")
    return render(request, "editcondition.html", context={"result": result, 'variables': varis })

# get conversion rule list
def newrule(request):

    # modified code
    from urllib import parse
    data_json = request.body
    data = parse.unquote_plus(data_json.decode('utf-8')).split('&')

    data_len = len(data)
    action = data[data_len - 1].split('=')[1]
    col_len = 7
    json_arr = []
    project_name = request.COOKIES.get('project_name')
    for i in range(data_len // col_len):
        srcpattern = data[i * col_len].split('=')[1]
        destpattern = data[i * col_len + 1].split('=')[1]
        enabled = True if data[i * col_len + 2].split('=')[1] == "1" or data[i * col_len + 2].split('=')[1] == True else False
        #case_sensitive = True if data[i * col_len + 3].split('=')[1] == "1" else False
        case_sensitive = True if data[i * col_len + 3].split('=')[1] == "1" or data[i * col_len + 3].split('=')[1] == "True" else False
        exceptions = data[i * col_len + 4].split('=')[1]
        priority = 1000 if data[i * col_len + 5].split('=')[1] == "" else data[i * col_len + 5].split('=')[1]
        no = data[i * col_len + 6].split('=')[1]

        if action == "remove":
            no = data[i*col_len].split('=')[1]
            srcpattern = data[i * col_len + 4].split('=')[1]
            delete = ConversionRule.objects.get(no=no)
            delete.delete()
        else:
            if action == "create":
                template = ConversionRule(srcpattern=srcpattern, destpattern=destpattern, enabled=enabled, case_sensitive=case_sensitive, exceptions=exceptions, priority=priority, project_name=project_name)
                template.save()
                no = template.no

            elif action == "edit":
                change = ConversionRule.objects.get(no=no)
                change.srcpattern = srcpattern
                change.destpattern = destpattern
                change.case_sensitive = case_sensitive
                change.enabled = enabled
                change.exceptions = exceptions
                change.priority = priority
                change.save()

        json_arr.append({
            "No": no,
            "Source Pattern": '<xmp>' + '"' + srcpattern + '"' + '</xmp>',
            "Dest Pattern": '<xmp>' + '"' + destpattern + '"' + '</xmp>',
            "Enable": enabled,
            "Case Sensitive": case_sensitive,
            "Exceptions": exceptions,
            "Priority": priority
        })
    return JsonResponse({
        "data": json_arr
    })
    exit()

    pass



def loadrulelist(request):
    project_name = request.COOKIES.get('project_name')
    data = ConversionRule.objects.raw(""
                           "SELECT "
                           "    * "                          
                           "FROM "
                           "    managetemplate_conversionrule "
                           "WHERE "
                           "    project_name = '{}'"
                           "ORDER BY "                           
                           "    priority;".format(project_name)
                           )
    data_list = list(data)
    json_arr = []
    for item in data_list:
        # no = item["no"]
        # srcpattern = item["srcpattern"]
        # destpattern = item["destpattern"]
        # enabled = item["enabled"]
        # case_sensitive = item["case_sensitive"]
        # exceptions = item["exceptions"]
        # priority = "" if item['priority'] == None else item["priority"]
        no = item.no
        srcpattern = item.srcpattern
        destpattern = item.destpattern
        enabled = item.enabled
        case_sensitive = item.case_sensitive
        exceptions = item.exceptions
        #priority = "" if item.priority == 10000 else item.priority
        priority = item.priority
        row = {
            "No": no,
            "Source Pattern": '<xmp>' + '"' + srcpattern + '"' + '</xmp>',
            "Dest Pattern": '<xmp>' + '"' + destpattern + '"' + '</xmp>',
            "Enable": enabled,
            "Case Sensitive": case_sensitive,
            "Exceptions": exceptions,
            "Priority": priority
        }
        json_arr.append(row)
    return JsonResponse({
        "data": json_arr
    })
    



def uploadfiles(request):
    #zipdata = request.POST['zip']
    #zipfilename = request.POST['zipfilename']

    fs = FileSystemStorage()
    if 'zipfilename' in request.POST:
        zipfilename = request.POST['zipfilename'].split('\\')[-1]

    else:
        zipfile = request.FILES['zipfile']

        isexist = fs.exists('uploads/' + zipfile.name)
        if isexist == True:
            fs.delete('uploads/' + zipfile.name)
        fs.save('uploads/' + zipfile.name, zipfile)
        zipfilename = zipfile.name

    #exceldata = request.POST['excel']

    if 'excelfilename' in request.POST:
        excelfilename = request.POST['excelfilename'].split('\\')[-1]
    else:
        excelfile = request.FILES['excelfile']
        isexist = fs.exists('uploads/' + excelfile.name)
        if isexist == True:
            fs.delete('uploads/' + excelfile.name)

        fs.save('uploads/' + excelfile.name, excelfile)
        excelfilename= excelfile.name

    success = ec.OK

    isvalidexcel = xlsutil.isexcelfile('uploads/' + excelfilename)
    if isvalidexcel == False:
        success = ec.InvalidExcel
        fs.delete('uploads/' + excelfilename)

    isvalidzip = ziputil.iszipfile('uploads/' + zipfilename)
    if isvalidzip == False:
        success = ec.InvalidZip
        fs.delete('uploads/' + zipfilename)

    if success != ec.OK:
        return JsonResponse({'success': success})
    cleartempfiles()

    if ziputil.unzip('uploads/' + zipfilename, 'uploads/origfiles') == False:
        return JsonResponse({'success': EC.UnZipFail})

    global valuemax
    valuemax = ziputil.filecount()

    seterrorstring("")

    success = xlsutil.configmap('uploads/' + excelfilename)
    if success != ec.OK:
        return JsonResponse({
            'success': success,
            'errormsg': geterrorstring()
        })

    #VF.objects.all().delete()
    fieldname = []
    datas = VF.objects.all()
    datas = list(datas)
    var_list = []
    for data in datas:
        var_list.append(data.name)

    for (k, v) in xlsutil.convmap.items():
        if k[0] == '$':
            fieldname.append(k)
            if k not in var_list:
                template = VF(name=k)
                template.save()


    data = {
        'success': success,
        'fields': fieldname,
        'errormsg': geterrorstring()
    }

    return JsonResponse(data)


def cleartempfiles():
    fs = FileSystemStorage()
    origfiles = [f for f in listdir('uploads/origfiles') if isfile(join('uploads/origfiles', f))]
    for i in range(len(origfiles)):
        fs.delete('uploads/origfiles/' + origfiles[i])

    destfiles = [f for f in listdir('uploads/destfiles') if isfile(join('uploads/destfiles', f))]
    for i in range(len(destfiles)):
        fs.delete('uploads/destfiles/' + destfiles[i])

    #fs.delete('static/result.zip')
    pass


def startconvert(request):
    data_json = request.body
    data = json.loads(data_json)
    zipfile = data['zip']
    excelfile = data['xls']
    savename = data['save']
    novalrule = data['novalrule']
    jsonoutput = data['jsonoutput']
    output_format = data['output_format']
    addptag = data['addptag']
    ordername = data['ordername']
    ordertype = data['ordertype']
    humanaction = data['humanaction']
    editorial_method = data['editorial_method']
    showEmptySection = data["showEmptySection"]

    project_name = request.COOKIES.get('project_name')

    success = ec.OK
    if zipfile == "" or excelfile == "":
        success = ec.EmptyFileName

    fs = FileSystemStorage()
    if fs.exists('uploads/' + excelfile) == False:
        success = ec.NoExistExcel
    elif ordername != "":
        xlsutil.orderupdate('uploads/' + excelfile, ordername)

    if fs.exists('uploads/' + zipfile) == False:
        success = ec.NoExistZip

    if success != ec.OK:
        return JsonResponse({'success': success})

    seterrorstring('')

    destfiles = [f for f in listdir('uploads/destfiles') if isfile(join('uploads/destfiles', f))]
    for i in range(len(destfiles)):
        fs.delete('uploads/destfiles/' + destfiles[i])

    success = ziputil.replacevariables('uploads/' + zipfile, savename, novalrule, output_format, addptag, project_name, ordername, ordertype, humanaction, editorial_method, showEmptySection)

    if isinstance(success, str) and 'excel_error' in success:
        err_var = success.replace('excel_error', '')
        err_msg = err_var + ' of condition list is not existed in the excel header'
        data = {
            'success': 'fail',
            'errormsg': err_msg
        }
        return JsonResponse(data)
    else:
        data = {
            'success': success,
            'errormsg': geterrorstring(),
            'download_root': get_download_root()
        }
        return JsonResponse(data)


def startdownload(request):
    #filleddata = dict(request.GET.items())
    #pypdftk.fill_form("uploads/invoice_template.pdf", filleddata, out_file="out.pdf")
    data = {'success':1}
    return JsonResponse(data)

def deletefiles(request):
    for f in listdir('static/result'):
        file_path = os.path.join('static/result', f)
        os.unlink(file_path)

    for f in listdir('static/csv'):
        file_path = os.path.join('static/csv', f)
        os.unlink(file_path)

    srcfiles = [f for f in listdir('uploads') if isfile(join('uploads', f))]
    for f in srcfiles:
        file_path = os.path.join('uploads', f)
        os.unlink(file_path)

    destfiles = [f for f in listdir('uploads/destfiles') if isfile(join('uploads/destfiles', f))]
    for f in destfiles:
        file_path = os.path.join('uploads/destfiles', f)
        os.unlink(file_path)

    origfiles = [f for f in listdir('uploads/origfiles') if isfile(join('uploads/origfiles', f))]
    for f in origfiles:
        file_path = os.path.join('uploads/origfiles', f)
        os.unlink(file_path)

    data = {'success': 1}
    return JsonResponse(data)


def saveascsv(request):
    project_name = request.COOKIES.get('project_name')
    data = CR.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    managetemplate_conversionrule "
                          "WHERE "
                          "    project_name = '{}'".format(project_name)
                          )

    # data = CR.objects.values()
    data_list = list(data)
    json_arr = []
    writer = csv.writer(open("static/csv/rules.csv", 'w', newline = '', encoding='utf-8'))
    #writer = csv.writer(open("static/csv/rules.csv", 'w', newline=''))
    writer.writerow(["Source Pattern", "Dest Pattern", "Enable", "Case Sensitive", "Exceptions", "Priority"])
    for item in data_list:
        row = [item.srcpattern, item.destpattern, item.enabled, item.case_sensitive, item.exceptions, item.priority]
        writer.writerow(row)
    file_path = "static/csv/rules.csv"

    if len(data_list) > 0:
        return JsonResponse({
            "success": 1,
            "download_csv": file_path
        })
    else:
        return JsonResponse({
            "success": 0
        })

# condition part

# get conversion rule list
def newcondition(request):
    project_name = request.COOKIES.get('project_name')

    # modified code
    from urllib import parse
    data_json = request.body
    data = parse.unquote_plus(data_json.decode('utf-8')).split('&')

    data_len = len(data)
    action = data[data_len - 1].split('=')[1]
    col_len = 3
    json_arr = []
    for i in range(data_len // col_len):
        condition_id = data[i * col_len].split('=')[1]
        # condition_content = data[i * col_len + 1].split('=')[1]
        condition_content = data[i * col_len + 1].replace(data[i * col_len + 1].split('=')[0] + "=", "")
        id = data[i * col_len + 2].split('=')[1]


        if action == "remove":
            id = data[i*col_len].split('=')[1]
            condition_id = data[i * col_len + 2].split('=')[1]
            delete = CD.objects.get(id=id)
            delete.delete()
        else:
            if action == "create":
                template = CD(condition_id=condition_id, condition_content=condition_content, project_name=project_name)
                template.save()
                id = template.id

            elif action == "edit":
                change = ConversionRule.objects.get(no=no)
                change.srcpattern = srcpattern
                change.destpattern = destpattern
                change.case_sensitive = case_sensitive
                change.enabled = enabled
                change.exceptions = exceptions
                change.priority = priority
                change.save()

        json_arr.append({
            "id": id,
            "Condition ID": condition_id,
            "Condition Content": condition_content
        })
    return JsonResponse({
        "data": json_arr
    })

def loadconditionlist(request):
    project_name = request.COOKIES.get('project_name')
    data = CD.objects.raw(""
                           "SELECT "
                           "    * "                          
                           "FROM "
                           "    managetemplate_condition "
                           "WHERE "
                           "    project_name = '{}'".format(project_name)
                        )
    data_list = list(data)
    json_arr = []
    for item in data_list:

        id = item.id
        condition_id = item.condition_id
        condition_content = item.condition_content

        row = {
            "id": id,
            "Condition ID": condition_id,
            "Condition Content": condition_content
        }
        json_arr.append(row)
    return JsonResponse({
        "data": json_arr
    })

def create_condition(request):
    name = request.POST.get('name')
    result = request.POST.get('result')
    project_name = request.COOKIES.get('project_name')
    new_condition = CD.objects.create(
        condition_id=name,
        condition_content=result,
        project_name=project_name,
    )
    new_condition.save()
    return redirect("viewconditions")


def saveconditioncsv(request):
    """Save condition to csv file."""
    project_name = request.COOKIES.get('project_name')
    data = CD.objects.raw(""
                             "SELECT "
                             "    * "
                             "FROM "
                             "    managetemplate_condition "
                             "WHERE "
                             "    project_name = '{}'".format(project_name)
                             )


    data_list = list(data)
    json_arr = []
    writer = csv.writer(open("static/csv/conditions.csv", 'w', newline = '', encoding='utf-8'))
    #writer = csv.writer(open("static/csv/rules.csv", 'w', newline=''))
    writer.writerow(["Condition ID", "Condition Content"])
    for item in data_list:
        row = [item.condition_id, item.condition_content]
        writer.writerow(row)
    file_path = "static/csv/conditions.csv"

    if len(data_list) > 0:
        return JsonResponse({
            "success": 1,
            "download_csv": file_path
        })
    else:
        return JsonResponse({
            "success": 0
        })

def viewprojects(request):
    return render(request, 'viewprojects.html')

def newproject(request):
    # modified code
    from urllib import parse
    data_json = request.body
    data = parse.unquote_plus(data_json.decode('utf-8')).split('&')

    data_len = len(data)
    action = data[data_len - 1].split('=')[1]
    col_len = 2
    json_arr = []
    for i in range(data_len // col_len):
        name = data[i * col_len].split('=')[1]

        id = data[i * col_len + 1].split('=')[1]

        if action == "remove":
            id = data[i * col_len].split('=')[1]
            name = data[i * col_len + 1].split('=')[1]
            delete = PJ.objects.get(id=id)
            delete.delete()
        else:
            if action == "create":
                template = PJ(name=name)
                template.save()
                id = template.id

            elif action == "edit":
                change = PJ.objects.get(id=id)
                change.name = name
                change.save()

        json_arr.append({
            "id": id,
            "Project Name": name
        })
    return JsonResponse({
        "data": json_arr
    })

def edit_project(request):
    return render(request, 'viewprojects.html')

def loadprojectlist(request):
    data = PJ.objects.raw(""
                           "SELECT "
                           "    * "
                           "FROM "
                           "    managetemplate_projects "
                           "ORDER BY "
                           "    name "
                           )
    data_list = list(data)
    json_arr = []
    for item in data_list:
        project_id = item.id
        project_name = item.name
        row = {
            "id": project_id,
            "Project Name": project_name
        }
        json_arr.append(row)

    return JsonResponse({
        "data": json_arr
    })

def viewvarconditions(request):
    return render(request, 'viewvarconditions.html')

def newvarcondition(request):
    pass
def loadvarconditionlist(request):
    project_name = request.COOKIES.get('project_name')
    data = VARCD.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    managetemplate_variablecondition "
                          "WHERE "
                          "    project_name = '{}'".format(project_name)
                          )
    data_list = list(data)
    json_arr = []
    for item in data_list:
        id = item.id
        variable_name = item.variable_name
        condition_content = item.condition_content
        use_excel_for_fulfill = item.use_excel_for_fulfill
        text_for_fulfill = item.text_for_fulfill
        use_excel_for_not_fulfill = item.use_excel_for_not_fulfill
        text_for_not_fulfill = item.text_for_not_fulfill

        row = {
            "id": id,
            "Variable Name": variable_name,
            "Condition Content": condition_content,
            "Use Excel for fulfill": use_excel_for_fulfill,
            "Text for fulfill": text_for_fulfill.replace("\n", "<br/>"),
            "Use Excel for not-fulfill": use_excel_for_not_fulfill,
            "Text for not-fulfill": text_for_not_fulfill.replace("\n", "<br/>"),

        }
        json_arr.append(row)
    return JsonResponse({
        "data": json_arr
    })

def addvarcondition(request):
    variables = VF.objects.values_list("name").order_by("name")
    variables = list(variables)
    varis = []
    for i in range(len(variables)):
        varis.append(variables[i][0])
    return render(request, 'addvarcondition.html', context={'variables': varis})

def create_varcondition(request):

    variable_name = request.POST.get('Variable-Name')
    result = request.POST.get('result')
    project_name = request.COOKIES.get('project_name')
    cond_fulfill_opt = request.POST.get('cond_fulfill_opt')
    if cond_fulfill_opt == 'from_excel':
        cond_fulfill_opt = True
    else:
        cond_fulfill_opt = False
    cond_fulfill_txt = request.POST.get('cond_fulfill_txt')
    cond_not_fulfill_opt = request.POST.get('cond_not_fulfill_opt')
    if cond_not_fulfill_opt == 'from_excel':
        cond_not_fulfill_opt = True
    else:
        cond_not_fulfill_opt = False
    cond_not_fulfill_txt = request.POST.get('cond_not_fulfill_txt')
    new_condition = VARCD.objects.create(
        variable_name=variable_name,
        condition_content=result,
        use_excel_for_fulfill=cond_fulfill_opt,
        text_for_fulfill=cond_fulfill_txt,
        use_excel_for_not_fulfill=cond_not_fulfill_opt,
        text_for_not_fulfill=cond_not_fulfill_txt,
        project_name=project_name,
    )
    new_condition.save()
    return redirect("viewvarconditions")
def edit_varcondition(request, id):
    result = VARCD.objects.get(id=id)

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
        result.use_excel_for_fulfill = request.POST.get('cond_fulfill_opt')
        if result.use_excel_for_fulfill == 'from_excel':
            result.use_excel_for_fulfill = True
        else:
            result.use_excel_for_fulfill = False
        result.text_for_fulfill = request.POST.get('cond_fulfill_txt')
        result.use_excel_for_not_fulfill = request.POST.get('cond_not_fulfill_opt')
        if result.use_excel_for_not_fulfill == 'from_excel':
            result.use_excel_for_not_fulfill = True
        else:
            result.use_excel_for_not_fulfill = False
        result.text_for_not_fulfill = request.POST.get('cond_not_fulfill_txt')
        result.save()
        return redirect("viewvarconditions")
    return render(request, "editvarcondition.html", context={"result": result, 'variables': varis })

def savevarconditioncsv(request):
    project_name = request.COOKIES.get('project_name')
    data = VARCD.objects.raw(""
                          "SELECT "
                          "    * "
                          "FROM "
                          "    managetemplate_variablecondition "
                          "WHERE "
                          "    project_name = '{}'".format(project_name)
                          )

    # data = CR.objects.values()
    data_list = list(data)
    json_arr = []
    writer = csv.writer(open("static/csv/variable_conditions.csv", 'w', newline='', encoding='utf-8'))
    # writer = csv.writer(open("static/csv/rules.csv", 'w', newline=''))
    writer.writerow(["Variable Name", "Condition Content", "Use Excel for fulfill", "Text for fulfill", "Use Excel for not-fulfill", "Text for not-fulfill"])
    for item in data_list:
        row = [item.variable_name, item.condition_content, item.use_excel_for_fulfill, item.text_for_fulfill.replace('\n', '--\\--'), item.use_excel_for_not_fulfill, item.text_for_not_fulfill.replace('\n', '--\\--')]
        writer.writerow(row)
    file_path = "static/csv/variable_conditions.csv"

    if len(data_list) > 0:
        return JsonResponse({
            "success": 1,
            "download_csv": file_path
        })
    else:
        return JsonResponse({
            "success": 0
        })

def newvarcondition(request):
    project_name = request.COOKIES.get('project_name')

    # modified code
    from urllib import parse
    data_json = request.body
    data = parse.unquote_plus(data_json.decode('utf-8')).split('&')

    data_len = len(data)
    action = data[data_len - 1].split('=')[1]
    col_len = 7
    json_arr = []
    for i in range(data_len // col_len):

        if action == "remove":
            id = data[i*col_len].split('=')[1]

            delete = VARCD.objects.get(id=id)
            json_arr.append({
                "id": delete.id,
                "Variable Name": delete.variable_name,
                "Condition Content": delete.condition_content,
                "Use Excel for fulfill": delete.use_excel_for_fulfill,
                "Text for fulfill": delete.text_for_fulfill.replace("\n", "<br/>"),
                "Use Excel for not-fulfill": delete.use_excel_for_not_fulfill,
                "Text for not-fulfill": delete.text_for_not_fulfill.replace("\n", "<br/>"),
            })
            delete.delete()
        elif action == "create":
            variable_name = data[i * col_len].split('=')[1]
            condition_content = data[i * col_len + 1].split('=')[1]
            use_excel_for_fulfill = data[i * col_len + 2].split('=')[1]
            text_for_fulfill = data[i * col_len + 3].split('=')[1].replace('--\\--', '\n')
            use_excel_for_not_fulfill = data[i * col_len + 4].split('=')[1]
            text_for_not_fulfill = data[i * col_len + 5].split('=')[1].replace('--\\--', '\n')

            template = VARCD(variable_name=variable_name,
                    condition_content=condition_content,
                    use_excel_for_fulfill=use_excel_for_fulfill,
                    text_for_fulfill=text_for_fulfill,
                    use_excel_for_not_fulfill=use_excel_for_not_fulfill,
                    text_for_not_fulfill=text_for_not_fulfill,
                    project_name=project_name)
            template.save()
            id = template.id
            json_arr.append({
                "id": id,
                "Variable Name": variable_name,
                "Condition Content": condition_content,
                "Use Excel for fulfill": use_excel_for_fulfill,
                "Text for fulfill": text_for_fulfill.replace('\n', '<br/>'),
                "Use Excel for not-fulfill": use_excel_for_not_fulfill,
                "Text for not-fulfill": text_for_not_fulfill.replace('\n', '<br/>'),
            })

    return JsonResponse({
        "data": json_arr
    })

# new permutation function (2020.09.12)
def permutation(request):
    return render(request, 'permutation/index.html')

def permutation_selectproject(request):
    data = PermutationProjects.objects.raw(""
                                           "SELECT "
                                           "    * "
                                           "FROM "
                                           "    managetemplate_permutationprojects "
                                           "ORDER BY "
                                           "    name "
                                           )
    data_list = list(data)
    arr = []
    for item in data_list:
        arr.append(item.name)

    return render(request, 'permutation/selectproject.html', context={'name_list': arr})

def permutation_viewprojects(request):
    return render(request, 'permutation/viewprojects.html')

def loadpermutationprojectlist(request):
    data = PermutationProjects.objects.raw(""
                           "SELECT "
                           "    * "
                           "FROM "
                           "    managetemplate_permutationprojects "
                           "ORDER BY "
                           "    name "
                           )
    data_list = list(data)
    json_arr = []
    for item in data_list:
        project_id = item.id
        project_name = item.name
        row = {
            "id": project_id,
            "Project Name": project_name
        }
        json_arr.append(row)

    return JsonResponse({
        "data": json_arr
    })

def newpermutationproject(request):
    # modified code
    from urllib import parse
    data_json = request.body
    data = parse.unquote_plus(data_json.decode('utf-8')).split('&')

    data_len = len(data)
    action = data[data_len - 1].split('=')[1]
    col_len = 2
    json_arr = []
    for i in range(data_len // col_len):
        name = data[i * col_len].split('=')[1]

        id = data[i * col_len + 1].split('=')[1]

        if action == "remove":
            id = data[i * col_len].split('=')[1]
            name = data[i * col_len + 1].split('=')[1]
            delete = PermutationProjects.objects.get(id=id)
            delete.delete()

            # delete permutationgeneral
            PermutationGeneral.objects.filter(project_name=name).delete()
            # delete permutationparagraphs
            PermutationParagraphs.objects.filter(project_name=name).delete()
        else:
            if action == "create":
                template = PermutationProjects(name=name)
                template.save()
                id = template.id

            elif action == "edit":
                change = PermutationProjects.objects.get(id=id)
                change.name = name
                change.save()

        json_arr.append({
            "id": id,
            "Project Name": name
        })
    return JsonResponse({
        "data": json_arr
    })

def permutation_uploadfiles(request):

    zipfile = request.FILES['zipfile']

    fs = FileSystemStorage()
    isexist = fs.exists('uploads/' + zipfile.name)
    if isexist == True:
        fs.delete('uploads/' + zipfile.name)
    filename = fs.save('uploads/' + zipfile.name, zipfile)

    isvalidzip = ziputil.iszipfile('uploads/' + zipfile.name)
    success = ec.OK
    if isvalidzip == False:
        success = ec.InvalidZip
        fs.delete('uploads/' + zipfile.name)

    if success != ec.OK:
        return JsonResponse({'success': success})

    data = {
        'success': success
    }

    return JsonResponse(data)

def edit_permutation_rules(request):
    project_name = request.COOKIES.get('permutation_project_name')

    data = PermutationGeneral.objects.raw(""
                                           "SELECT "
                                           "    * "
                                           "FROM "
                                           "    managetemplate_permutationgeneral "
                                           "WHERE "
                                           "    project_name = '{}'".format(project_name)
                                           )
    data_list = list(data)
    update_status = False
    apply_to_all_para = False
    default_permutation_mode = 'ALL_NOT_PERMUTABLE'
    default_rand_from = 1
    default_rand_to = 1
    project_min_words = 0
    project_max_words = 0
    for item in data_list:
        update_status = item.update_status
        apply_to_all_para = item.apply_to_all_para
        default_rand_from = item.rand_from
        default_rand_to = item.rand_to
        project_min_words = item.min_words
        project_max_words = item.max_words

    json_arr = []
    if update_status:
        data = PermutationParagraphs.objects.raw(""
                                              "SELECT "
                                              "    * "
                                              "FROM "
                                              "    managetemplate_permutationparagraphs "
                                              "WHERE "
                                              "    project_name = '{}'".format(project_name)
                                              )
        data_list = list(data)

        for i, item in enumerate(data_list):
            section_name = item.section_name
            section_visibility = item.section_visibility
            type = item.type
            number_of_elements = item.number_of_elements
            permutation_mode = item.permutation_mode
            rand_from = item.rand_from
            rand_to = item.rand_to
            content = item.content
            if type == 'section':
                element_type = 'paragraphs'
            else:
                element_type = 'elements'

            min_words = item.min_words
            max_words = item.max_words

            row = {
                "no": str(i+1),
                "section_name": section_name,
                "section_visibility": section_visibility,
                "type": type,
                "number_of_elements": number_of_elements,
                "permutation_mode": permutation_mode,
                "rand_from": rand_from,
                "rand_to": rand_to,
                "content": content,
                "element_type": element_type,
                "min_words": min_words,
                "max_words": max_words
            }
            json_arr.append(row)
    context = {
        'update_status': update_status,
        'apply_to_all_para': apply_to_all_para,
        'default_permutation_mode': default_permutation_mode,
        'default_rand_from': default_rand_from,
        'default_rand_to': default_rand_to,
        'data': json_arr,
        'total_row': len(json_arr),
        'min_words': project_min_words,
        'max_words': project_max_words
    }

    return render(request, 'permutation/edit_permutation_rules.html', context=context)

def uploadtxt(request):
    txtfile = request.FILES['txtfile']

    print('test2')

    fs = FileSystemStorage()
    isexist = fs.exists('uploads/' + 'sample.txt')
    if isexist == True:
        fs.delete('uploads/' + 'sample.txt')
    filename = fs.save('uploads/' + 'sample.txt', txtfile)

    data = {
        'success': True
    }

    return JsonResponse(data)

def processtxt(request):
    data = txtutil.extract_paragraphs('uploads/' +'sample.txt')

    update_status = True
    context = {
        'update_status': update_status,
        'data': data,
        'total_row': len(data)
    }
    return render(request, 'permutation/edit_permutation_rules.html', context=context)

def update_permutation_rule(request):
    project_name = request.COOKIES.get('permutation_project_name')
    data_json = request.body
    data = json.loads(data_json)

    total_row = int(data['total_row'])

    # delete permutationgeneral
    PermutationGeneral.objects.filter(project_name=project_name).delete()

    # delete permutationparagraphs
    PermutationParagraphs.objects.filter(project_name=project_name).delete()

    section_words_info = {}
    for i in range(total_row):
        index = str(i + 1)
        section_visibility = False

        permutation_mode = data['cnt_par[{}][permutation_mode]'.format(index)]
        rand_from = data['cnt_par[{}][rand_from]'.format(index)]
        rand_to = data['cnt_par[{}][rand_to]'.format(index)]
        section_name = data['cnt_par[{}][section_name]'.format(index)]
        type = data['cnt_par[{}][type]'.format(index)]
        number_of_elements = data['cnt_par[{}][number_of_elements]'.format(index)]
        if 'cnt_par_enabled_{}'.format(index) in data:
            section_visibility = True
        content = data['cnt_par[{}][p_contents]'.format(index)]

        min_words, max_words = 0, 0
        if type == 'paragraphs':
            min_words, max_words = txtutil.get_min_max_words_of_paragraph(content, rand_from, rand_to)
            section_words_info[section_name]['min_words'].append(min_words)
            section_words_info[section_name]['max_words'].append(max_words)

        template = PermutationParagraphs(project_name=project_name, section_name=section_name, section_visibility=section_visibility,
                                         type=type, number_of_elements=number_of_elements, permutation_mode=permutation_mode,rand_from=rand_from, rand_to=rand_to, content=content,
                                         min_words=min_words, max_words=max_words
                                  )
        template.save()

        if type == 'section':
            section_words_info[section_name] = {}
            section_words_info[section_name]['rand_from'] = rand_from
            section_words_info[section_name]['rand_to'] = rand_to
            section_words_info[section_name]['min_words'] = []
            section_words_info[section_name]['max_words'] = []

    section_min_words_list = []
    section_max_words_list = []

    for section_name, value_list in section_words_info.items():
        rand_from = value_list.get('rand_from')
        rand_to = value_list.get('rand_to')
        min_words_list = value_list.get('min_words')
        max_words_list = value_list.get('max_words')

        min_words, max_words = txtutil.get_min_max_words_of_section(rand_from, rand_to, min_words_list, max_words_list)
        section_min_words_list.append(min_words)
        section_max_words_list.append(max_words)
        PermutationParagraphs.objects.filter(project_name=project_name, type='section', section_name=section_name).update(min_words=min_words, max_words=max_words)

    project_min_words = sum(section_min_words_list)
    project_max_words = sum(section_max_words_list)

    template = PermutationGeneral(project_name=project_name, update_status=True, apply_to_all_para=False, rand_from=1, rand_to=1, min_words=project_min_words, max_words=project_max_words)
    template.save()

    data = {
        'success': True
    }

    return JsonResponse(data)


def permutation_startconvert(request):

    data_json = request.body
    data = json.loads(data_json)
    zipfile = data['zip']
    # jsonoutput = data['jsonoutput']
    addptag = data['addptag']
    output_format = data['output_format']

    project_name = request.COOKIES.get('permutation_project_name')


    success = ec.OK
    if zipfile == "":
        success = ec.EmptyFileName

    fs = FileSystemStorage()

    if fs.exists('uploads/' + zipfile) == False:
        success = ec.NoExistZip

    if success != ec.OK:
        return JsonResponse({'success': success})

    cleartempfiles()
    seterrorstring('')

    success = permutation_ziputil.replacevariables('uploads/' + zipfile, output_format, addptag, project_name)
    if isinstance(success, str) and 'excel_error' in success:
        err_var = success.replace('excel_error', '')
        err_msg = err_var + ' of condition list is not existed in the excel header'
        data = {
            'success': 'fail',
            'errormsg': err_msg
        }
        return JsonResponse(data)
    else:
        data = {
            'success': success,
            'errormsg': geterrorstring(),
            'download_root': get_download_root()
        }
        return JsonResponse(data)

def reset_template(request):
    project_name = request.COOKIES.get('permutation_project_name')

    # delete permutationgeneral
    PermutationGeneral.objects.filter(project_name=project_name).delete()

    # delete permutationparagraphs
    PermutationParagraphs.objects.filter(project_name=project_name).delete()

    data = {
        'success': True
    }

    return JsonResponse(data)

def check_process(request):
    global valuemax
    valuenow = ziputil.get_valuenow()
    print(valuenow)
    print(valuemax)
    data = {
        'success': 1,
        'valuemax': valuemax,
        'valuenow': valuenow
    }
    return JsonResponse(data)


def deleteDuplicates(request):
    data_json = request.body
    data = json.loads(data_json)
    dup_ids = data['dup_ids']

    ConversionRule.objects.filter(no__in=dup_ids).delete()

    return JsonResponse({
        'success': 1        
    })

def cleanText(request):
    return render(request, 'cleanText.html')

def uploadfiles_clean(request):
   

    fs = FileSystemStorage()
    if 'zipfilename' in request.POST:
        zipfilename = request.POST['zipfilename'].split('\\')[-1]

    else:
        zipfile = request.FILES['zipfile']

        isexist = fs.exists('uploads/' + zipfile.name)
        if isexist == True:
            fs.delete('uploads/' + zipfile.name)
        fs.save('uploads/' + zipfile.name, zipfile)
        zipfilename = zipfile.name

    success = ec.OK

    isvalidzip = ziputil.iszipfile('uploads/' + zipfilename)
    if isvalidzip == False:
        success = ec.InvalidZip
        fs.delete('uploads/' + zipfilename)

    if success != ec.OK:
        return JsonResponse({'success': success})
    cleartempfiles()

    if ziputil.unzip('uploads/' + zipfilename, 'uploads/origfiles') == False:
        return JsonResponse({'success': EC.UnZipFail})
    seterrorstring("")

    data = {
        'success': success,        
        'errormsg': geterrorstring()
    }

    return JsonResponse(data)

def startconvert_clean(request):
    data_json = request.body
    data = json.loads(data_json)
    zipfile = data['zip']
   
   

    success = ec.OK
    if zipfile == "":
        success = ec.EmptyFileName

    fs = FileSystemStorage()    
    if fs.exists('uploads/' + zipfile) == False:
        success = ec.NoExistZip

    if success != ec.OK:
        return JsonResponse({'success': success})

    seterrorstring('')

    destfiles = [f for f in listdir('uploads/destfiles') if isfile(join('uploads/destfiles', f))]
    for i in range(len(destfiles)):
        fs.delete('uploads/destfiles/' + destfiles[i])

    success = ziputil.cleanAllText()
    
    data = {
        'success': success,
        'errormsg': geterrorstring(),
        'download_root': get_download_root()
    }
    return JsonResponse(data)
