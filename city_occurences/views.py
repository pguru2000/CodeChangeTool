from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core.files.storage import FileSystemStorage
import os
from os import listdir
from os.path import isfile, join
import json
import re
import unicodedata

from utils import city_xlsmanager as xlsutil
from utils.errorcode import ErrorCode as ec
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring
from utils.download_root import get_download_root

UPLOAD_PATH = 'uploads/slug_generator/'

# Create your views here.
def index(request):
    return render(request, 'city_occurences/index.html')

def uploadfiles(request):    

    fs = FileSystemStorage()    

    if 'excelfilename' in request.POST:
        excelfilename = request.POST['excelfilename'].split('\\')[-1]
    else:
        excelfile = request.FILES['excelfile']
        isexist = fs.exists(UPLOAD_PATH + excelfile.name)
        if isexist == True:
            fs.delete(UPLOAD_PATH + excelfile.name)

        fs.save(UPLOAD_PATH + excelfile.name, excelfile)
        excelfilename= excelfile.name

    success = ec.OK

    isvalidexcel = xlsutil.isexcelfile(UPLOAD_PATH + excelfilename)
    if isvalidexcel == False:
        success = ec.InvalidExcel
        fs.delete(UPLOAD_PATH + excelfilename)
    
    if success != ec.OK:
        return JsonResponse({'success': success})

    # cleartempfiles()
    seterrorstring("")

    success = xlsutil.configmap(UPLOAD_PATH + excelfilename)
    if success != ec.OK:
        return JsonResponse({
            'success': success,
            'errormsg': geterrorstring()
        })

    fieldname = []
    
    for (k, v) in xlsutil.convmap.items():
        # if k[0] == '$':
        fieldname.append(k)

    print(fieldname)
            

    data = {
        'success': success,
        'fields': fieldname,
        'errormsg': geterrorstring()
    }

    return JsonResponse(data)

def cleartempfiles():
    fs = FileSystemStorage()
    origfiles = [f for f in listdir(UPLOAD_PATH) if isfile(join(UPLOAD_PATH, f))]
    for i in range(len(origfiles)):
        fs.delete(UPLOAD_PATH + origfiles[i])

def startconvert(request):
    data_json = request.body
    data = json.loads(data_json)
    
    excelfile = data['xls']
    concat_1 = data['concat_1']
    concat_2 = data['concat_2']
    concat_3 = data['concat_3']

    print(concat_1)
    print(concat_2)
    print(concat_3)

    success = xlsutil.concatStart(excelfile, concat_1, concat_2, concat_3)

    data = {
        'success': success,
        'errormsg': geterrorstring(),
        'download_root': get_download_root()
    }
    return JsonResponse(data)

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def deletefiles(request):
    for f in listdir('static/result'):
        file_path = os.path.join('static/result', f)
        os.unlink(file_path)

    destfiles = [f for f in listdir('uploads/slug_generator') if isfile(join('uploads/slug_generator', f))]
    for f in destfiles:
        file_path = os.path.join('uploads/slug_generator', f)
        os.unlink(file_path)  

    data = {'success': 1}
    return JsonResponse(data)