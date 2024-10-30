from django.shortcuts import render

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect

from permutation.models import NewPermutationProjects
from permutation.models import NewPermutationGeneral
from permutation.models import NewPermutationParagraphs

from utils import new_permutation_zipmanager as new_permutation_ziputil
from utils import new_permutation_txtmanager as new_txtutil

from utils.errorcode import ErrorCode as ec
from utils.errorcode import geterrorstring
from utils.errorcode import seterrorstring
from utils.download_root import get_download_root

from os import listdir
from os.path import isfile, join
import json

# Create your views here.
from django.http import HttpResponse,JsonResponse



# new permutation function (2020.09.12)
def new_permutation(request):
    return render(request, 'new_permutation/index.html')

def new_permutation_selectproject(request):
    project_list = NewPermutationProjects.objects.values_list("name")

    project_list = list(project_list)
    arr = []
    for i in range(len(project_list)):
        arr.append(project_list[i][0])

    return render(request, 'new_permutation/selectproject.html', context={'name_list': arr})

def new_permutation_viewprojects(request):
    return render(request, 'new_permutation/viewprojects.html')

def new_loadpermutationprojectlist(request):
    data = NewPermutationProjects.objects.raw(""
                           "SELECT "
                           "    * "
                           "FROM "
                           "    permutation_newpermutationprojects "
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

def new_newpermutationproject(request):
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
            delete = NewPermutationProjects.objects.get(id=id)
            delete.delete()

            # delete permutationgeneral
            NewPermutationGeneral.objects.filter(project_name=name).delete()
            # delete permutationparagraphs
            NewPermutationParagraphs.objects.filter(project_name=name).delete()
        else:
            if action == "create":
                template = NewPermutationProjects(name=name)
                template.save()
                id = template.id

            elif action == "edit":
                change = NewPermutationProjects.objects.get(id=id)
                change.name = name
                change.save()

        json_arr.append({
            "id": id,
            "Project Name": name
        })
    return JsonResponse({
        "data": json_arr
    })

def new_permutation_uploadfiles(request):

    zipfile = request.FILES['zipfile']

    fs = FileSystemStorage()
    isexist = fs.exists('uploads/' + zipfile.name)
    if isexist == True:
        fs.delete('uploads/' + zipfile.name)
    filename = fs.save('uploads/' + zipfile.name, zipfile)

    isvalidzip = new_permutation_ziputil.iszipfile('uploads/' + zipfile.name)
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

def new_edit_permutation_rules(request):
    project_name = request.COOKIES.get('new_permutation_project_name')

    data = NewPermutationGeneral.objects.raw(""
                                           "SELECT "
                                           "    * "
                                           "FROM "
                                           "    permutation_newpermutationgeneral "
                                           "WHERE "
                                           "    project_name = '{}'".format(project_name)
                                           )
    data_list = list(data)
    update_status = False

    for item in data_list:

        update_status = item.update_status
        permute_sections = item.permute_sections
        not_permute_conditional_sections = item.not_permute_conditional_sections
        permutation_mode_section = item.permutation_mode_section
        sections_rand_from = item.sections_rand_from
        sections_rand_to = item.sections_rand_to
        project_min_words = item.min_words
        project_max_words = item.max_words
        normal_sections_txt = item.normal_sections_txt
        count_normalsections = item.count_normalsections

    json_arr = []
    if update_status:
        data = NewPermutationParagraphs.objects.raw(""
                                              "SELECT "
                                              "    * "
                                              "FROM "
                                              "    permutation_newpermutationparagraphs "
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
            para_type = item.para_type

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
                "max_words": max_words,
                "para_type": para_type
            }
            json_arr.append(row)
        normal_sections = {
            "permute_sections": permute_sections,
            "not_permute_conditional_sections": not_permute_conditional_sections,
            "permutation_mode": permutation_mode_section,
            "rand_from": sections_rand_from,
            "rand_to": sections_rand_to,
            "texts": normal_sections_txt,
            "count": count_normalsections
        }
        context = {
            'update_status': update_status,
            'data': json_arr,
            'total_row': len(json_arr),
            'min_words': project_min_words,
            'max_words': project_max_words,
            'normal_sections': normal_sections
        }
    else:
        context = {
            'update_status': update_status
        }

    return render(request, 'new_permutation/edit_permutation_rules.html', context=context)

def new_uploadtxt(request):
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

def new_processtxt(request):
    data, normal_sections = new_txtutil.extract_paragraphs('uploads/' +'sample.txt')

    update_status = True
    context = {
        'update_status': update_status,
        'data': data,
        'total_row': len(data),
        'normal_sections': normal_sections
    }
    return render(request, 'new_permutation/edit_permutation_rules.html', context=context)

def new_update_permutation_rule(request):
    project_name = request.COOKIES.get('new_permutation_project_name')
    data_json = request.body
    data = json.loads(data_json)

    permute_sections = False
    not_permute_conditional_sections = False

    total_row = int(data['total_row'])
    permutation_mode_section = data['permutation_mode_section']
    sections_rand_from = data['sections_rand_from']
    sections_rand_to = data['sections_rand_to']
    normal_sections_txt = data['normal_sections_txt']
    if 'permute_sections' in data:
        permute_sections = True
    if 'not_permute_conditional_sections' in data:
        not_permute_conditional_sections = True
    count_normalsections = data['count_normalsections']

    # delete permutationgeneral
    NewPermutationGeneral.objects.filter(project_name=project_name).delete()

    # delete permutationparagraphs
    NewPermutationParagraphs.objects.filter(project_name=project_name).delete()

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
        para_type = data['cnt_par[{}][permutation_pos]'.format(index)]

        min_words, max_words = 0, 0
        if type == 'paragraphs':
            min_words, max_words = new_txtutil.get_min_max_words_of_paragraph(content, rand_from, rand_to)
            section_words_info[section_name]['min_words'].append(min_words)
            section_words_info[section_name]['max_words'].append(max_words)

        template = NewPermutationParagraphs(project_name=project_name, section_name=section_name, section_visibility=section_visibility,
                                         type=type, number_of_elements=number_of_elements, permutation_mode=permutation_mode,rand_from=rand_from, rand_to=rand_to, content=content,
                                         min_words=min_words, max_words=max_words, para_type=para_type
                                  )
        template.save()

        if type == 'section':
            section_words_info[section_name] = {}
            section_words_info[section_name]['rand_from'] = rand_from
            section_words_info[section_name]['rand_to'] = rand_to
            section_words_info[section_name]['min_words'] = []
            section_words_info[section_name]['max_words'] = []

    section_min_words_list_special = []
    section_max_words_list_special = []

    section_min_words_list_normal = []
    section_max_words_list_normal = []

    for section_name, value_list in section_words_info.items():
        
        rand_from = value_list.get('rand_from')
        rand_to = value_list.get('rand_to')
        min_words_list = value_list.get('min_words')
        max_words_list = value_list.get('max_words')        

        min_words, max_words = new_txtutil.get_min_max_words_of_section(rand_from, rand_to, min_words_list, max_words_list)

        if 'section' in section_name.lower():
            section_min_words_list_normal.append(min_words)
            section_max_words_list_normal.append(max_words)
        else:
            section_min_words_list_special.append(min_words)
            section_max_words_list_special.append(max_words)
        NewPermutationParagraphs.objects.filter(project_name=project_name, type='section', section_name=section_name).update(min_words=min_words, max_words=max_words)

    if permute_sections == True:
        project_min_words_normal, project_max_words_normal = new_txtutil.get_min_max_words_of_section(sections_rand_from, sections_rand_to, section_min_words_list_normal, section_max_words_list_normal)
        
    else:
        project_min_words_normal = sum(section_min_words_list_normal)
        project_max_words_normal = sum(section_max_words_list_normal)

    project_min_words_special = sum(section_min_words_list_special)
    project_max_words_special = sum(section_max_words_list_special)

    project_min_words = project_min_words_normal + project_min_words_special
    project_max_words = project_max_words_normal + project_max_words_special

    template = NewPermutationGeneral(project_name=project_name, update_status=True,
                                     min_words=project_min_words, max_words=project_max_words,
                                     permute_sections=permute_sections, permutation_mode_section=permutation_mode_section,
                                     sections_rand_from=sections_rand_from, sections_rand_to=sections_rand_to,
                                     normal_sections_txt=normal_sections_txt, count_normalsections=count_normalsections, not_permute_conditional_sections=not_permute_conditional_sections)
    template.save()

    data = {
        'success': True
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



def new_permutation_startconvert(request):

    data_json = request.body
    data = json.loads(data_json)
    zipfile = data['zip']
    jsonoutput = data['jsonoutput']
    addptag = data['addptag']

    project_name = request.COOKIES.get('new_permutation_project_name')


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

    success = new_permutation_ziputil.replacevariables('uploads/' + zipfile, jsonoutput, addptag, project_name)
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

def new_reset_template(request):
    project_name = request.COOKIES.get('new_permutation_project_name')

    # delete permutationgeneral
    NewPermutationGeneral.objects.filter(project_name=project_name).delete()

    # delete permutationparagraphs
    NewPermutationParagraphs.objects.filter(project_name=project_name).delete()

    data = {
        'success': True
    }

    return JsonResponse(data)