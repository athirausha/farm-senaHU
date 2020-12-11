from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .token_generator import account_activation_token,password_reset_token,Invite_token
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import smtplib
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

import re
import datetime
from datetime import date

from datetime import datetime
from datetime import timedelta

from Base.models import Base, Login, Basecolumns, Basedetails, Profile, Calculation,designation,\
    user_List, permissions, notification_Messages,Report,Reportcontent,pdfReport, Group_model_primary, Group_model_secondary
from Base.forms import ProfileForm
import openpyxl,xlrd
import pandas as pd
import os

from reportlab.lib.pagesizes import A4, inch

from reportlab.lib import colors

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from itertools import islice
import itertools


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def index(request):
    user = Login.objects.get(id=request.session['user_id'])
    user_email = user.email
    account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
    designations=designation.objects.all()
    sub_tbl = Group_model_secondary.objects.all()
    tmp_menu_pk = []
    for item in sub_tbl:
        tmp_menu_pk.append(item.secondary_tables_id)
    menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

    login_obj = Login.objects.all().exclude(id=request.session['user_id'])

    # FETCHING USER DETAILS FROM USER LIST TABLE
    permissions_list = user_List.objects.filter(user_id=user_email).values('table_id')
    permitted_tables = []
    for item in permissions_list:
        permitted_tables.append(item['table_id'])
    permitted_tables = Base.objects.filter(pk__in=permitted_tables).values('pk', 'base_name')

    pro = Profile.objects.filter(log_fk=request.session['user_id'])
    # Profile pic avilable or not
    profile_pic = ''
    if len(list(pro)) !=0:
        if pro[0].user_image == None:
            profile_pic = 'media/user.jpg'
        else:
            profile_pic = pro[0].user_image.url
    else:
        profile_pic = 'media/user.jpg'

    nti_msg = notification_Messages.objects.filter(Q(reciever_id=user_email) & Q(status=1))\
        .values('pk', 'heading', 'message', 'sender_id')
    final_nti_msg = []
    for item in nti_msg:
        if Profile.objects.filter(log_fk=item['sender_id']).count() == 1:
            pic_data = Profile.objects.get(log_fk=item['sender_id'])
            if pic_data.user_image == None:
                dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                       'pic': 'media/user.jpg'}
                final_nti_msg.append(dic)
            else:
                dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                       'pic': pic_data.user_image.url}
                final_nti_msg.append(dic)
        else:
            dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'], 'pic': 'media/user.jpg'}
            final_nti_msg.append(dic)

    nti_count = len(list(nti_msg))

    # REPORT and permitted report
    tmp_rids  = []
    rp = Report.objects.filter(created_by=user_email).values('pk')
    for item in rp:
        tmp_rids.append(item['pk'])
    print(tmp_rids)

    permissions_list = user_List.objects.filter(user_id=user_email).values('role')
    rep_role=[]
    for item in permissions_list:
        rep_role.append(item['role'])
    print(rep_role)

    rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).count()
    if rolse_data >= 1:
        per_rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).values('pk')
        tmp  = []
        for item in per_rolse_data:
            tmp.append(item['pk'])
        print('tmp')
        print(tmp)
        r_id=user_List.objects.filter(Q(user_id=user_email)& Q(role__in=tmp)).values('report_id')

        for item in r_id:
            tmp_rids.append(item['report_id'])
        print(tmp_rids)
    reports = Report.objects.filter(pk__in=tmp_rids).values('pk','Reportname')
    if request.session.has_key('user_id'):

        return render(request, 'table.html', {'menus': menus, 'pro': pro, 'permitted_tables': permitted_tables,\
                                              'login_obj': login_obj, 'user': user, 'profile_pic': profile_pic,
                                              'nti_count': nti_count, 'nti_msg': final_nti_msg,'reports':reports,
                                              'account_details':account_details,'designations':designations})
    return HttpResponseRedirect('/login')


def Register(request):
    try:
        if request.method == 'POST':
            name = request.POST['fname']
            email = request.POST['email']
            mobile = request.POST['mobile']
            password = request.POST['password']
            cpassword = request.POST['cpassword']
            company = request.POST['company']
            if password != cpassword:
                messages.success(request, 'Password Mismatch')
            elif name == '' or email == '' or mobile == '' or password == '' or cpassword == '' or company == '':
                messages.success(request, 'All Fileds Are Mandatory')
            elif len(mobile) != 10:
                messages.success(request, 'Mobile Number IS  Not Valid')
            elif not email_validation(email):
                messages.success(request, 'Email IS Not Valid')
            else:
                check_exist = Login.objects.filter(email=email).exists()
                if check_exist == False:
                    user = Login(name=name, phone=mobile, password=password, email=email, company_name=company,
                                 account_type='company_account', profile='Administer')
                    user.save()
                    if user.id > 0:
                        current_site = get_current_site(request)
                        email_subject = 'Activate Your Account'
                        message = render_to_string('activate_account.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
                        to_email = user.email
                        email = EmailMessage(email_subject, message, to=[to_email])
                        email.send()
                        # return HttpResponseRedirect('/verify')
                        messages.success(request, 'We have sent you an email, please confirm'
                                                  ' your email address to complete registration')
                # return HttpResponse('email id already exist')
                else:
                    messages.success(request, 'Email id already exist')
        return render(request, 'register.html')
    except Exception as e:
        print(e)
        return HttpResponse(e)
def personal_registration(request):
    try:
        if request.method == 'POST':
            name = request.POST['fname']
            email = request.POST['email']
            mobile = request.POST['mobile']
            password = request.POST['password']
            cpassword = request.POST['cpassword']


            if password != cpassword:
                messages.success(request, 'Password Mismatch')
            elif name == '' or email == '' or mobile == '' or password == '' or cpassword == '':
                messages.success(request, 'All Fileds Are Mandatory')
            elif len(mobile) != 10:
                messages.success(request, 'Mobile Number IS  Not Valid')
            elif not email_validation(email):
                messages.success(request, 'Email IS Not Valid')
            else:
                check_exist = Login.objects.filter(email=email).exists()
                if check_exist == False:
                    user = Login(name=name, phone=mobile, password=password, email=email,account_type='individual')
                    user.save()
                    if user.id > 0:
                        current_site = get_current_site(request)
                        email_subject = 'Activate Your Account'
                        message = render_to_string('activate_account.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
                        to_email = user.email
                        email = EmailMessage(email_subject, message, to=[to_email])
                        email.send()
                        # return HttpResponseRedirect('/verify')
                        messages.success(request, 'Account Created')

                # return HttpResponse('email id already exist')
                else:
                    messages.success(request, 'We have sent you an email, please confirm'
                                            ' your email address to complete registration')

        return render(request,'personalreg.html')
    except Exception as e:
        print(e)
        return HttpResponse(e)

def Register_users_load(request):

    try:
        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email
        menus = Base.objects.filter(created_by=user_email)
        company_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
        login_obj = Login.objects.all().exclude(id=request.session['user_id'])
        pro = Profile.objects.filter(log_fk=request.session['user_id'])
        designations=designation.objects.all()
        # Profile pic avilable or not
        profile_pic = ''
        if len(list(pro)) !=0:
            if pro[0].user_image == None:
                profile_pic = 'media/user.jpg'
            else:
                profile_pic = pro[0].user_image.url
        else:
            profile_pic = 'media/user.jpg'
        return render(request,'company_reg.html',{'account_details':company_details,'menus': menus,
                                   'profile_pic': profile_pic,'pro': pro,'user':user,'login_obj':login_obj,
                                   'designations':designations})
    except Exception as e:
        print(e)
        return HttpResponse(e)

def Register_users(request):
    try:
        if request.method == 'POST':
            name = request.POST['fname']
            email = request.POST['email']
            mobile = request.POST['mobile']
            password = request.POST['password']
            cpassword = request.POST['cpassword']
            company = request.POST['company']
            role = request.POST.get('profile_reg_user')
            if password != cpassword:
                messages.success(request, 'Password Mismatch')
                return redirect('/company_ind_reg_load')
            elif name == '' or email == '' or mobile == '' or password == '' or cpassword == '' or company == '' or role == '':
                messages.success(request, 'All Fileds Are Mandatory')
                return redirect('/company_ind_reg_load')
            elif len(mobile) != 10:
                messages.success(request, 'Mobile Number IS  Not Valid')
                return redirect('/company_ind_reg_load')
            elif not email_validation(email):
                messages.success(request, 'Email IS Not Valid')
                return redirect('/company_ind_reg_load')
            else:
                check_exist = Login.objects.filter(email=email).exists()
                if check_exist == False:
                    user = Login(name=name, phone=mobile, password=password, email=email, company_name=company,role=role, account_type='company_individual')
                    user.save()
                    if user.id > 0:
                        current_site = get_current_site(request)
                        email_subject = 'Activate Your Account'
                        message = render_to_string('activate_users_account.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
                        to_email = user.email
                        email = EmailMessage(email_subject, message, to=[to_email])
                        email.send()
                        # return HttpResponseRedirect('/verify')
                        messages.success(request, 'Account Created')
                        return redirect('/company_ind_reg_load')

                # return HttpResponse('email id already exist')
                else:
                    messages.success(request, 'Email id already exist')
                    return redirect('/company_ind_reg_load')

        return render(request,'company_reg.html')
    except Exception as e:
        print(e)
        return HttpResponse(e)

def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = Login.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        Login(request, user)
        # return render(request,'login.html')
        return HttpResponseRedirect('/login')
    # return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


def fn_login(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            check_exist = Login.objects.filter(email=username).exists()
            if check_exist == False:
                messages.success(request, 'User not Exist')
                return HttpResponseRedirect('/login')
            login_obj = Login.objects.filter(email=username).values('pk','email','name','is_disabled','disable_period','password','disable_period_end')
            request.session['user_id'] = login_obj[0]['pk']
            # print(login_obj[0]['disable_period_end'])
            if login_obj[0]['password'] == password:

                if login_obj[0]['is_disabled'] == 'true':
                    if login_obj[0]['disable_period_end'] == datetime.today().date():
                        Login.objects.filter(id=request.session['user_id']).update(is_disabled='No',disable_period='Unknown',disable_period_end='Unknown')
                        return HttpResponseRedirect('/index')
                    else:
                        messages.success(request, 'This Account will get active on '+ login_obj[0]['disable_period_end'])
                        return redirect('/login')
                return HttpResponseRedirect('/index')
            messages.success(request, 'Wrong password')
            return render(request, "login.html")
        return render(request, "login.html")
    except Exception as e:
        print(e)


def Logout(request):
    # s=request.session['user_id']
    # s.delete()
    # session_destroy()
    try:
        if request.session.has_key('user_id'):
            # del request.session['user_id']
            request.session.flush()
            return HttpResponseRedirect('/login')
        else:
            return HttpResponseRedirect('/login')
    except Exception as e:
        return HttpResponse(e)


def Basecreation(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            createdby = user.email
            bname = request.POST['bname']
            tname = request.POST['tname']
            table_type = request.POST['table_type']
            table_discription = request.POST['table_discription']
            table_purpose = request.POST['table_purpose']
            table_bcp = request.POST['table_bcp']
            tags = request.POST['tags']

            alls = Base.objects.filter(Q(base_name=bname) & Q(created_by=createdby)).values('base_name').count()
            if alls == 0:
                base_tbl_id = Base.objects.create(base_name=bname, created_by=createdby, technical_name=tname,
                                    table_type=table_type, discription=table_discription,
                                    purpose=table_purpose, bcp=table_bcp, tags=tags)
                rs = Base.objects.filter(created_by=createdby).values('base_name', 'pk')
                print('PK : ' + str(base_tbl_id.pk))
                print('Name : ' + str(base_tbl_id.base_name))
                return JsonResponse({'Result' : 1, 'RD': list(rs), 'Status': True, "Id": base_tbl_id.pk, 'Name': base_tbl_id.base_name})
            else:
                return JsonResponse({"Result": 0})
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse('Not a POST request')


# ADDING NEW COLUMNS IF NO COLUMNS FOUND
def Addcolumns(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            colname = request.POST['colname']
            type_d = request.POST['type_d']
            valnul = request.POST['v_null']
            col_siz=request.POST['col_size']
            tech_nam=request.POST['tech_namee']
            fk = request.POST['fk']

            createdby = login_id.email
            alls = Base.objects.filter(Q(base_name=fk) & Q(created_by=createdby)).values('pk')
            Basecolumns.objects.create(c_name=colname, base_fk=alls[0]['pk'], d_type=type_d,d_size=col_siz,t_name=tech_nam,nul_type=valnul)
            return HttpResponse('Basecol Done')
        except Exception as e:
            return HttpResponse(e)


# SAVING THE RELATION COLUMN
def save_relation_column(request):
    if request.method == 'POST':
        try:
            user = Login.objects.get(id=request.session['user_id'])
            login_user = user.email
            # COLUMN PRIMARY KEY
            colum_pk = request.POST['key']
            # TABLE PRIMARY KEY
            table_pk = request.POST['m_key']
            # NAME OF THE COLUMN
            name = request.POST['name']
            # MAXIMUM NUMBER OF ROWS HAVE
            max_row = request.POST['mx']

            data_column = Basecolumns.objects.filter(pk=colum_pk).values('pk', 'c_name', 'base_fk', 'd_type',
                                                                         'calc_type')
            data_column = list(data_column)
            if data_column[0]['d_type'].isnumeric():
                Basecolumns.objects.create(c_name=data_column[0]['c_name'], base_fk=table_pk,
                                           d_type=data_column[0]['base_fk'], calc_type=data_column[0]['calc_type'])
            else:
                Basecolumns.objects.create(c_name=data_column[0]['c_name'], base_fk=table_pk,
                                           d_type=data_column[0]['base_fk'], calc_type=data_column[0]['d_type'])

            max_row = int(max_row) + 1
            # THE ID OF NEW COLUMN CREATED
            f = Basecolumns.objects.latest('id')
            for item in range(1, int(max_row)):
                Basedetails.objects.create(c_v='No', bc_fk=f, row_num=item)
            return JsonResponse({'data': 'Success Relation column'})
        except Exception as e:
            return HttpResponse(e)


# ADDING VALUES TO COLUMNS
def Adddetails(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email
            table_id = request.POST['table_id']
            imp = request.POST['imp']
            d1 = request.POST['d1']
            rr = request.POST['rr']
            max_row = request.POST['mx']
            max_row = int(max_row) + 1
            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name
            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()
            if data == 1:
                if rr != '':
                    nul=Basecolumns.objects.filter(pk=rr).values('nul_type')
                    if nul[0]['nul_type']=='NULL' and d1 == "":
                        Basedetails.objects.create(c_v='Empty', bc_fk=rr, row_num=max_row)
                    else:
                        Basedetails.objects.create(c_v=d1, bc_fk=rr, row_num=max_row)
                    # return HttpResponse('New Record Added')
                    return JsonResponse({'data':max_row})

            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('add_data')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['add_data'] == 'true':
                        if rr != '':
                            nul=Basecolumns.objects.filter(pk=rr).values('nul_type')
                            if nul[0]['nul_type'] == 'NULL':
                                Basedetails.objects.create(c_v='Empty', bc_fk=rr, row_num=max_row)
                            else:
                                Basedetails.objects.create(c_v=d1, bc_fk=rr, row_num=max_row)
                            if int(imp) == 1:
                                print("Notification Sending......")
                                notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id))\
                                    .values('user_id')
                                msg = str(login_user) + ' add new record to ' + str(table_real_name)
                                for x in notfy:
                                    if x['user_id'] != login_user:
                                        notification_sender(sender_id=request.session['user_id'],
                                                            user_email=x['user_id'], status=1,
                                                            heading="New Record Added", message=msg)
                                # SENDING TO TABLE OWNER
                                notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                                    status=1, heading="New Record Added", message=msg)
                                # return HttpResponse('New Record Added')
                                return JsonResponse({'data':max_row})
                            else:
                                print("Notification Not Sending......")
                                return HttpResponse('Value Added')
            else:
                return JsonResponse({'Result': "You don't have permission for performing this action"})
        except Exception as e:
            return HttpResponse(e)


def data_image_upload(request):
    if request.method == "POST":
        try:
            table_id = request.POST['id']
            uploaded_file = request.FILES['files']
            image_columns_id = request.POST['image_columns_id']
            max_row = int(request.POST['max_row'])
            max_row = int(max_row) + 1

            print("image_columns_id :- " + str(image_columns_id))
            print("table_id :- " + str(table_id))
            print("max_row :- " + str(max_row))

            fs = FileSystemStorage()--
            name = fs.save(uploaded_file.name, uploaded_file)
            name = 'media/' + name

            Basedetails.objects.create(c_v=name, bc_fk=image_columns_id, row_num=max_row)

            return HttpResponse('Done')
        except Exception as e:
            return HttpResponse(e)


def cal_add_details(request):
    if request.method == "POST":
        try:
            max_row = request.POST['mx']
            calc_column_id = request.POST['relation_clc']
            d1 = request.POST.getlist('d1[]')
            rr = request.POST.getlist('rr[]')
            print("==== ADD DETAILS CALC VALUE AUTO UPDATE SECTION ===")
            print("D1 : ")
            print(d1)
            print("RR : ")
            print(rr)

            ft_equation = Calculation.objects.filter(fk_column=calc_column_id).values('pk', 'equ', 'fk_column',
                                                                                      'fk_table', 'createdby',
                                                                                      'equ_normal', 'type_of_calc',
                                                                                      'const_position')

            fr_ids = str(ft_equation[0]['equ']).split(',')
            fr_vals = str(ft_equation[0]['equ_normal']).split(',')
            print("fr_ids : ")
            print(fr_ids)
            print("fr_vals : ")
            print(fr_vals)
            # ['15', '+', 'const', '']
            for item in range(0, len(fr_ids)-1, 2):
                # 15
                tmp = fr_ids[item]
                # ['8', '9', '14', '15']
                for x in range(0, len(rr)):
                    if fr_ids[item] == 'const':
                        # ['plant date', '+', '1', '']
                        fr_ids[item] = int(fr_vals[item])
                        print("const")
                    elif rr[x] == fr_ids[item]:
                        # ['23', '34', '2020-07-28', '2020-07-20']
                        fr_ids[item] = d1[x]
                        print('yes')
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                if tmp == fr_ids[item]:
                    print("--- More Options ---")
                    data = Basecolumns.objects.filter(pk=int(fr_ids[item])).values('d_type', 'pk')
                    print("Data --> ")
                    if len(list(data)) != 0:
                        print(data)
                        if data[0]['d_type'] == 'Calc':
                            print("--- Checking Data Type ---")
                            tmp = int(tmp)
                            max_tmp = int(max_row) + 1
                            print("tmp :  " + str(tmp))
                            print("max_tmp : " + str(max_tmp))
                            data_value = Basedetails.objects.filter(Q(bc_fk=tmp) & Q(row_num=max_tmp)).values('c_v')
                            print("Data Value")
                            print(data_value)
                            data_value = data_value[0]['c_v']
                            print("data_value : " + str(data_value))
                            fr_ids[item] = data_value
                    else:
                        fr_ids[item] = 0

            print("####### Update fr_ids : ########")
            print(fr_ids)

            if ft_equation[0]['type_of_calc'] == 'Date_With_Const':
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                if ft_equation[0]['const_position'] == 1:
                    x1 = fr_ids[0]
                    op = fr_ids[1]
                    x2 = fr_ids[2]
                    result = days_betwenn_constant(x1, x2, op)
                    print("1st Time result : " + str(result))
                    for item in range(3, len(fr_ids) - 1, 2):
                        op = fr_ids[item]
                        x2 = fr_ids[item + 1]
                        result = days_betwenn_constant(result, x2, op)
                    print("Final Result : " + str(result))
                    max_row = int(max_row) + 1
                    Basedetails.objects.create(c_v=result, bc_fk=calc_column_id, row_num=max_row)
                    return HttpResponse('Adddetails to calc value')
                else:
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@")
                    x1 = fr_ids[0]
                    op = fr_ids[1]
                    x2 = fr_ids[2]
                    print('x1 : ')
                    print(x1)
                    print('x2 : ')
                    print(x2)
                    result = days_betwenn_constant(x1, x2, op)
                    print('####################################')
                    print("1st Time result : " + str(result))
                    for item in range(3, len(fr_ids) - 1, 2):
                        op = fr_ids[item]
                        x2 = fr_ids[item + 1]
                        result = days_betwenn_constant(result, x2, op)
                    print("Final Result : " + str(result))
                    max_row = int(max_row) + 1
                    Basedetails.objects.create(c_v=result, bc_fk=calc_column_id, row_num=max_row)
                    return HttpResponse('Adddetails to calc value')
            elif ft_equation[0]['type_of_calc'] == 'Date_Calc':
                x1 = fr_ids[0]
                op = fr_ids[1]
                x2 = fr_ids[2]
                result = days_between(x1, x2, op)
                print("1st Time result : " + str(result))
                for item in range(3, len(fr_ids) - 1, 2):
                    op = fr_ids[item]
                    x2 = fr_ids[item + 1]
                    result = days_between(result, x2, op)
                print("Final Result : " + str(result))
                max_row = int(max_row) + 1
                Basedetails.objects.create(c_v=result, bc_fk=calc_column_id, row_num=max_row)
                return HttpResponse('Adddetails to calc value')
            else:
                x1 = fr_ids[0]
                x2 = fr_ids[2]
                op = fr_ids[1]

                result = operation(x1, x2, op)
                print("1st Time result : " + str(result))
                for item in range(3, len(fr_ids)-1, 2):
                    op = fr_ids[item]
                    x2 = fr_ids[item + 1]
                    result = operation(result, x2, op)

                print("Final Result : " + str(result))
                max_row = int(max_row) + 1
                Basedetails.objects.create(c_v=result, bc_fk=calc_column_id, row_num=max_row)
                return HttpResponse('Adddetails to calc value')

        except Exception as e:
            return HttpResponse(e)


# BASIC TABLE VIEW FUNCTIONALITY
def Details(request, pkp):
    try:
        if request.session.has_key('user_id'):
            user_in = Login.objects.get(id=request.session['user_id'])
            user_email = user_in.email
            reports = Report.objects.filter(created_by=user_email).values('pk', 'Reportname')
            account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
            login_obj = Login.objects.all().exclude(id=request.session['user_id'])
            sub_tbl = Group_model_secondary.objects.all()
            designations=designation.objects.all()
            tmp_menu_pk = []
            for item in sub_tbl:
                tmp_menu_pk.append(item.secondary_tables_id)
            menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

            pro = Profile.objects.filter(log_fk=request.session['user_id'])

            # PROFILE PIC AVAILABLE OR NOT
            profile_pic = ''
            if len(list(pro)) != 0:
                if pro[0].user_image == None:
                    profile_pic = 'media/user.jpg'
                else:
                    profile_pic = pro[0].user_image.url
            else:
                profile_pic = 'media/user.jpg'
            # REPORT and permitted report
            tmp_rids  = []
            rp = Report.objects.filter(created_by=user_email).values('pk')
            for item in rp:
                tmp_rids.append(item['pk'])
            print(tmp_rids)

            permissions_list = user_List.objects.filter(user_id=user_email).values('role')
            rep_role=[]
            for item in permissions_list:
                rep_role.append(item['role'])
            print(rep_role)

            rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).count()
            if rolse_data >= 1:
                per_rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).values('pk')
                tmp  = []
                for item in per_rolse_data:
                    tmp.append(item['pk'])
                print('tmp')
                print(tmp)
                r_id=user_List.objects.filter(Q(user_id=user_email)& Q(role__in=tmp)).values('report_id')

                for item in r_id:
                    tmp_rids.append(item['report_id'])
                print(tmp_rids)
            reports = Report.objects.filter(pk__in=tmp_rids).values('pk','Reportname')
            # NOTIFICATION FENCING
            nti_msg = notification_Messages.objects.filter(Q(reciever_id=user_email) & Q(status=1)) \
                .values('pk', 'heading', 'message', 'sender_id')
            final_nti_msg = []
            for item in nti_msg:
                if Profile.objects.filter(log_fk=item['sender_id']).count() == 1:
                    pic_data = Profile.objects.get(log_fk=item['sender_id'])
                    if pic_data.user_image == None:
                        dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                               'pic': 'media/user.jpg'}
                        final_nti_msg.append(dic)
                    else:
                        dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                               'pic': pic_data.user_image.url}
                        final_nti_msg.append(dic)
                else:
                    dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                           'pic': 'media/user.jpg'}
                    final_nti_msg.append(dic)
            nti_count = len(list(nti_msg))

            #  CHECKING PERMISSIONS
            tbl_data = Base.objects.filter(Q(created_by=user_email) & Q(pk=pkp)).values('pk')
            tbl_data_count = Base.objects.filter(Q(created_by=user_email) & Q(pk=pkp)).count()
            print(tbl_data)
            pr_check = 'True'
            if tbl_data_count == 0:
                pr_check = 'False'
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=user_email) & Q(table_id=pkp)).values('role')
                permitted_rolse = []

                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                tbl_data = permissions.objects.filter(pk__in=permitted_rolse).values('add_user', 'create_tables',
                                                                                     'add_data', 'delete_data',
                                                                                     'update_data', 'add_col',
                                                                                     'delete_col', 'update_col')
                return redirect('/index')
            Message_me = Basecolumns.objects.filter(base_fk=pkp).count()
            pros = Base.objects.filter(pk=pkp).values('base_name', 'pk')
            info = Base.objects.get(id=pkp)
            # filter
            col = []
            base_col = Basecolumns.objects.filter(base_fk=pkp).values('pk', 'c_name')
            base_col = list(base_col)
            for items in base_col:
                col.append(items['pk'])
            base_details = Basedetails.objects.filter(bc_fk__in=col).values('c_v', 'bc_fk').distinct()
            basedetails = list(base_details)
            col_count = []
            for items in base_details:
                b_names = Basedetails.objects.filter(c_v=items['c_v']).count()
                col_count.append(b_names)
            # filter end
            # to list allowed users
            allowed_users=user_List.objects.filter(table_id=pkp).values('user_id')
            if Message_me == 0:
                return render(request, 'view.html', {'status': 0, 'menus': menus, 'pros': pros, 'user': user_in,
                                                     'column': base_col, 'c_values': basedetails, 'count': col_count,
                                                     'profile_pic': profile_pic, 'nti_count': nti_count,
                                                     'nti_msg': final_nti_msg, 'id': pkp,'account_details':account_details,
                                                     'allowed_users': allowed_users, 'reports': reports,'login_obj':login_obj,
                                                     'designations':designations,'cdate':datetime.today().date()})
            else:
                # Fetching the columns related to master table
                alls = Basecolumns.objects.filter(base_fk=pkp).values('base_name', 'c_name', 'base_fk', 'pk', 'd_type',
                                                                      'd_size', 'nul_type')
                array_dtype = []
                for item in alls:
                    array_dtype.append(item['d_type'])

                tmp = []
                # filtering columns primary key
                for item in alls:
                    tmp.append(item['pk'])

                mapp_value = []
                map_filter_value = None

                # Fetching values related to column
                querysets = Basedetails.objects.filter(bc_fk__in=tmp).values('c_v', 'bc_fk', 'pk', 'row_num').\
                    order_by('row_num', 'bc_fk')

                # Final result of row values
                column_values = []
                # Final result of row value Id
                colum_values_id =[]
                # Final reslut of row number
                column_row_val = []
                # Final Result column data type for adding file input in front
                column_data_type = []

                # converting fetched basedetails object to list
                querysets = list(querysets)

                for item in querysets:
                    tmp_type = Basecolumns.objects.get(pk=item['bc_fk'])
                    column_data_type.append(tmp_type.d_type)
                    column_values.append(item['c_v'])
                    colum_values_id.append(item['pk'])
                    column_row_val.append(item['row_num'])

                # Length of
                length_base_details = len(column_values)
                length_base_column = Basecolumns.objects.filter(base_fk=pkp).count()
                total = int(length_base_details/length_base_column)

                # Last row number ---> appending to table body as id
                if len(column_row_val) == 0:
                    max_row = 0
                else:
                    max_row = max(column_row_val)
                mylist = zip(column_values, colum_values_id, column_row_val, column_data_type)
                mylist_length = len(column_values)
                print("**************************************")
                print(pr_check)

                # FETCHING GROUP MODELS IF SELECTED TABLE IS PRIMARY MASTER OF THAT GROUP
                additional_tbls_name = []
                additional_tbls_id = []
                if Group_model_primary.objects. \
                        filter(Q(table_id_primary=pkp) & Q(created_users_id=request.session['user_id'])).count() > 0:
                    print("FETCHING GROUP MODELS IF SELECTED TABLE IS PRIMARY MASTER OF THAT GROUP")
                    primary_tbl = Group_model_primary.objects.filter(table_id_primary=pkp). \
                        values('pk', 'table_id_primary', 'created_users_id', 'Group_name')
                    primary_tbl_array = []
                    for item in primary_tbl:
                        primary_tbl_array.append(item['pk'])

                    secondary_tbl = Group_model_secondary.objects.filter(primary_table_fk__in=primary_tbl_array). \
                        values('pk', 'secondary_tables_id', 'secondary_tables_name')

                    if len(list(secondary_tbl)) > 0:
                        for item in secondary_tbl:
                            additional_tbls_id.append(item['secondary_tables_id'])
                            additional_tbls_name.append(item['secondary_tables_name'])

            return render(request, 'view.html', {'column': base_col, 'c_values': basedetails, 'count': col_count,
                                                  'mylist_length': mylist_length, 'pro': pro,
                                                  'user': user_in, 'map_filter_value': map_filter_value, 'info': info,
                                                  'tytime':'Time', 'tydate': 'Date', 'ttext': 'String', 'tt': 'Text',
                                                  'Calc': 'Calc', 'tnumeric': 'Numeric', 'tnum': 'Number',
                                                  'max_row': max_row, 'mylist': mylist, 'bc': length_base_column,
                                                  'id': pkp, 'menus': menus, 'alls': alls, 'pros': pros,
                                                  'profile_pic': profile_pic, 'nti_count': nti_count, 'timage': 'Image',
                                                  'nti_msg': final_nti_msg, 'tbl_data': tbl_data, 'pr_check': pr_check,
                                                  'true': 'true', 't': 'True', 'allowed_users': allowed_users,
                                                 'reports': reports,'account_details':account_details,'login_obj':login_obj,
                                                 'additional_tbls': zip(additional_tbls_id, additional_tbls_name),\
                                                 'designations':designations,'cdate':datetime.today().date()})

        return HttpResponseRedirect('/login')
    except Exception as e:
        return HttpResponse(e)


# FETCHING RELATION COLUMNS OF THE TABLE
def filter_columns_for_relation(request):
    if request.method == "POST":
        try:
            fk = request.POST['fk']
            result = Basecolumns.objects.filter(base_fk=fk).values('c_name', 'pk')
            return JsonResponse({'Result': list(result)})
        except Exception as e:
            return HttpResponse(e)


# FETCHING RELATION TABLE OF THE TABLE
def relation_maters(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email
            data = Base.objects.filter(created_by=user_email).values('fk', 'pk', 'base_name')
            # list_fk = [ item['fk'] for item in data ]
            # data = Base.objects.filter(pk__in=list_fk).values('pk', 'base_name')
            return JsonResponse({'Result': list(data)})
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse('Request not POST')


# SAVING THE RELATION COLUMN
def save_relation_column_page_one(request):
    if request.method == 'POST':
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email
            # COLUMN PRIMARY KEY
            colum_pk = request.POST['key']
            # TABLE PRIMARY KEY
            table_pk = request.POST['m_key']
            table_pk = Base.objects.filter(Q(base_name=table_pk) & Q(created_by=user_email)).values('pk', 'base_name')
            table_pk = table_pk[0]['pk']
            # NAME OF THE COLUMN
            name = request.POST['name']
            data_column = Basecolumns.objects.filter(pk=colum_pk).values('pk', 'c_name', 'base_fk', 'd_type',
                                                                         'calc_type')
            data_column = list(data_column)
            if data_column[0]['d_type'].isnumeric():
                Basecolumns.objects.create(c_name=data_column[0]['c_name'], base_fk=table_pk,
                                           d_type=data_column[0]['base_fk'], calc_type=data_column[0]['calc_type'])
            else:
                Basecolumns.objects.create(c_name=data_column[0]['c_name'], base_fk=table_pk,
                                           d_type=data_column[0]['base_fk'], calc_type=data_column[0]['d_type'])

            return JsonResponse({'data': 'Success'})

        except Exception as e:
            return HttpResponse(e)


# CREATING NEW COLUMN IN TABLE
def Newcol(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            fk = int(request.POST['fk'])
            colname = request.POST['colname']
            max_row = request.POST['mx']
            col_size = request.POST['col_size']
            col_type = request.POST['col_type']
            nul_type = request.POST['nul_type']

            table_real_name = Base.objects.get(id=fk)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=fk)).count()
            status_of_up = 0
            permitted_rolse = []
            if data == 1:
                status_of_up = 1
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=fk)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('add_col')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['add_col'] == 'true':
                        status_of_up = 2
            else:
                return JsonResponse({'Result': "You don't have permission for performing this action"})

            if status_of_up == 1 or status_of_up == 2:
                Basecolumns.objects.create(c_name= colname, base_fk=fk, d_type=col_type ,d_size=col_size,nul_type=nul_type)
                querysets = Basecolumns.objects.filter(base_fk=fk).values('pk')
                a = []
                for item in querysets:
                    a.append(item['pk'])
                max_row = int(max_row) + 1
                f = Basecolumns.objects.latest('id')
                for item in range(1,int(max_row)):
                    if  col_type == 'Numeric' or col_type == 'Number':
                        Basedetails.objects.create(c_v='0', bc_fk=f, row_num=item)
                    elif  col_type == 'Date':
                        Basedetails.objects.create(c_v=datetime.today().date(), bc_fk=f, row_num=item)
                    else:
                        Basedetails.objects.create(c_v='No', bc_fk=f, row_num=item)

            if status_of_up == 2:
                print("Notification Sending......")
                notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=fk)).values('user_id')
                msg = str(login_user) + ' Created New Column in  ' + str(table_real_name)
                for x in notfy:
                    if x['user_id'] != login_user:
                        notification_sender(sender_id=request.session['user_id'],
                                            user_email=x['user_id'], status=1,
                                            heading="New Column Created", message=msg)
                # SENDING TO TABLE OWNER
                notification_sender(sender_id=request.session['user_id'], user_email=table_owner, status=1,
                                    heading="New Column Created", message=msg)
            else:
                pass
        except Exception as e:
            return HttpResponse(e)


def referanfce_col_filter(request):
    if request.method == "POST":
        try:
            col_id = request.POST['col_id']
            data_set = Basecolumns.objects.filter(pk=col_id).values('base_name', 'c_name', 'base_fk', 'pk', 'd_type')
            col = ''
            for x in data_set:
                col = x['c_name']
            col = col.split('(')
            print(col)

            # '6', 'Nothing', '2020-06-01', '2020-06-01', 'Qr Code', '1', '2'

            mapp_value = []
            for item in data_set:
                if item['d_type'].isnumeric():
                    mapp_value.append(item['d_type'])
                if len(mapp_value) > 0:
                    print("mapp value : " + mapp_value[0])
                    print("c_name : " + col[0].strip())
                    mapp_filter_columns = Basecolumns.objects.filter(
                        Q(base_fk__in=mapp_value) & Q(c_name=col[0].strip())) \
                        .values('base_name', 'c_name', 'base_fk', 'pk', 'd_type')
                    # '3', 'Nothing', '2020-06-01', '2020-06-01', 'Bay Name', 'Text', '1'
                    # '4', 'Nothing', '2020-06-01', '2020-06-01', 'Qr Code', 'Numeric', '1'

                    mapp_filter_arry = []
                    for item in mapp_filter_columns:
                        mapp_filter_arry.append(item['pk'])
                        print("x---> " + str(item['pk']))
                        # '3'
                        # '4'
                    filter_value = Basedetails.objects.filter(bc_fk__in=mapp_filter_arry).values('c_v', 'bc_fk', 'pk',
                                                                                                 'row_num').order_by(
                        'row_num',
                        'bc_fk')

                    # '1', 'Nothing', '1', '4', '1'
                    # '2', 'Nothing', 'BAY 1', '3', '1'
                    # '3', 'Nothing', 'BAY 2', '3', '2'
                    # '4', 'Nothing', '2', '4', '2'

                    return JsonResponse({'filter_value': list(filter_value)})
        except Exception as e:
            return HttpResponse(e)


def inline_type_sub_table(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            login_user = user.email

            key = request.POST['key']  # 184

            table_id = request.POST['base_id']

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()

            opr_status = False
            if data == 1:
                opr_status = True
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('update_data')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['update_data'] == 'true':
                        opr_status = True

            if opr_status:

                querysets = Basecolumns.objects.filter(pk=key).values('pk', 'd_type', 'c_name', 'd_size', 'nul_type')
                querysets = list(querysets)

                relation_val_pk = []
                relation_val = []

                if len(querysets) > 0:
                    if querysets[0]['d_type'].isnumeric():
                        """
                        +----+-----------+------------------+--------------------+--------------+--------+---------+--------+
                        | id | base_name | base_create_date | base_modified_date | c_name       | d_type | base_fk | d_size |
                        +----+-----------+------------------+--------------------+--------------+--------+---------+--------+
                        | 36 | Nothing   | 2020-06-25       | 2020-06-25         | Student Name | String |       7 |     40 |
                        | 37 | Nothing   | 2020-06-25       | 2020-06-25         | Student Age  | Number |       7 |     40 |
                        | 38 | Nothing   | 2020-06-25       | 2020-06-25         | Place        | String |       7 |     40 |
                        +----+-----------+------------------+--------------------+--------------+--------+---------+--------+
                        """
                        col = querysets[0]['c_name']
                        col = col.split('(')
                        base = Basecolumns.objects.filter(Q(base_fk=querysets[0]['d_type']) &
                                                      Q(c_name=col[0].strip())).values('base_name', 'c_name',
                                                                                       'base_fk', 'pk', 'd_type','d_size')

                        for item in base:
                            relation_val_pk.append(item['pk'])

                relation = Basedetails.objects.filter(bc_fk__in=relation_val_pk).values('c_v', 'bc_fk', 'pk', 'row_num')
                for item in relation:
                    relation_val.append(item['c_v'])
                return JsonResponse({'Rate': 1, 'Result': querysets, 'Relation': relation_val})
            else:
                return JsonResponse({'Rate': 0})

        except Exception as e:
            return HttpResponse(e)


def inline_type(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            login_user = user.email

            key = request.POST['key']  # 184

            table_id = request.POST['base_id']

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()
            opr_status = False
            if data == 1:
                opr_status = True
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('update_data')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['update_data'] == 'true':
                        opr_status = True

            if opr_status:
                # 184 | Nothing   | Appu |    42 |       2
                querysets = Basedetails.objects.filter(pk=key).values('c_v', 'bc_fk', 'pk', 'row_num')\
                    .order_by('row_num', 'bc_fk')

                querysets = list(querysets)
                colvalues=list(querysets)

                """
                +----+-----------+------------------+--------------------+----------------------------------+--------+---------+--------+
                | id | base_name | base_create_date | base_modified_date | c_name                           | d_type | base_fk | d_size |
                +----+-----------+------------------+--------------------+----------------------------------+--------+---------+--------+
                | 42 | Nothing   | 2020-06-25       | 2020-06-25         | Student Name ( Student Details ) | 7      |       8 |     40 |
                +----+-----------+------------------+--------------------+----------------------------------+--------+---------+--------+
                """

                querysets = Basecolumns.objects.filter(pk=querysets[0]['bc_fk']).values('pk', 'd_type', 'c_name',
                                                                                        'd_size', 'nul_type')
                querysets = list(querysets)

                relation_val_pk = []
                relation_val = []
                relation_row = []

                if len(querysets) > 0:
                    if querysets[0]['d_type'].isnumeric():
                        """
                        +----+-----------+------------------+--------------------+--------------+--------+---------+--------+
                        | id | base_name | base_create_date | base_modified_date | c_name       | d_type | base_fk | d_size |
                        +----+-----------+------------------+--------------------+--------------+--------+---------+--------+
                        | 36 | Nothing   | 2020-06-25       | 2020-06-25         | Student Name | String |       7 |     40 |
                        | 37 | Nothing   | 2020-06-25       | 2020-06-25         | Student Age  | Number |       7 |     40 |
                        | 38 | Nothing   | 2020-06-25       | 2020-06-25         | Place        | String |       7 |     40 |
                        +----+-----------+------------------+--------------------+--------------+--------+---------+--------+
                        """
                        col = querysets[0]['c_name']
                        col = col.split('(')
                        base = Basecolumns.objects.filter(Q(base_fk=querysets[0]['d_type']) &
                                                      Q(c_name=col[0].strip())).values('base_name', 'c_name',
                                                                                       'base_fk', 'pk', 'd_type','d_size')

                        for item in base:
                            relation_val_pk.append(item['pk'])

                relation = Basedetails.objects.filter(bc_fk__in=relation_val_pk).values('c_v', 'bc_fk', 'pk', 'row_num')
                for item in relation:
                    relation_val.append(item['c_v'])
                    relation_row.append(item['row_num'])
                return JsonResponse({'Rate': 1, 'Result': querysets, 'Relation': relation_val, 'row': relation_row,
                                     'col_values': colvalues})
            else:
                return JsonResponse({'Rate': 0})

        except Exception as e:
            return HttpResponse(e)


def inline_update_image(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            login_user = user.email

            details_id = request.POST['id']
            table_id = request.POST['base_id']
            uploaded_file = request.FILES['files']

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            name = '/media/' + name

            update = 0

            base_data = Basedetails.objects.get(pk=details_id)
            if base_data.c_v != name:
                base_data.c_v = name
                update = update + 1
            if update > 0:
                base_data.save()
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                print('permision rolse : ')
                print(permitted_rolse)
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)).values('user_id')
                msg = str(login_user) + ' Updated a Record in ' + str(table_real_name)
                print(msg)
                for x in notfy:
                    if x['user_id'] != login_user:
                        notification_sender(sender_id=request.session['user_id'],
                                            user_email=x['user_id'], status=1,
                                            heading="Record Updated", message=msg)
                # SENDING TO TABLE OWNER
                notification_sender(sender_id=request.session['user_id'], user_email=table_owner, status=1,
                                    heading="Record Updated", message=msg)

                return JsonResponse({'path': name, 'path_u':details_id})

        except Exception as e:
            return HttpResponse(e)


def Updatedetails(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            login_user = user.email
            details_ids=[]
            details_id = request.POST['id']
            # details_ids.append(details_id)
            # print(details_id)
            table_id = request.POST['base_id']
            det_id=Basecolumns.objects.filter(d_type=table_id).values('pk')
            print(det_id)
            detailids=[]
            for items in det_id:
               detailids.append(items['pk'])
            print(detailids)
            base_data = Basedetails.objects.get(pk=details_id)
            base_data_c_val=base_data.c_v
            print(base_data_c_val)

            basedats_cv= Basedetails.objects.filter(Q(bc_fk__in=detailids) & Q(c_v=base_data_c_val)).values('pk','row_num','bc_fk','c_v')
            print(basedats_cv)

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name
            # ref_data_id=Basecolumns.objects.filter(d_type=table_id).values('pk')

            """
            bc_fk = 3
            row_num = 3
            """
            column_id = base_data.bc_fk
            row_no = base_data.row_num
            update = 0
            rs_pk = []
            rs_val = []
            cv_data=[]
            for item in basedats_cv:
                cv_data.append(item['pk'])

            d_count=Basedetails.objects.filter(Q(pk__in=cv_data) | Q(pk=details_id)).count()
            if d_count >= 1:
                Basedetails.objects.filter(pk= details_id).update(c_v=request.POST['d'])
                Basedetails.objects.filter(pk__in=cv_data).update(c_v=request.POST['d'])



                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                print('permision rolse : ')
                print(permitted_rolse)
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)).values('user_id')
                msg = str(login_user) + ' Updated  a Record in ' + str(table_real_name)
                print(msg)
                for x in notfy:
                    if x['user_id'] != login_user:
                        notification_sender(sender_id=request.session['user_id'],
                                            user_email=x['user_id'], status=1,
                                            heading="Record Updated", message=msg)
                # SENDING TO TABLE OWNER
                notification_sender(sender_id=request.session['user_id'], user_email=table_owner, status=1,
                                    heading="Record Updated", message=msg)

                """
                # id	equ	fk_table	fk_column	createdby	equ_normal
                1	3,+,2,	1	20	jitheeshemmanuel@gmail.com	Maths,+,Science,
                2	2,-,20,	1	21	jitheeshemmanuel@gmail.com	Science,-,SUM,
                """
                data = Calculation.objects.filter(fk_table=table_id).values('equ', 'fk_column', 'equ_normal',
                                                                            'type_of_calc', 'const_position')
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                print(data)
                data_tmp = list(data)
                for item in data_tmp:
                    """
                    1---> [   3   +   2   '']
                    2---> [   2   -   20  '']
                    """
                    tmp_list = str(item['equ']).split(',')
                    equ_normal = str(item['equ_normal']).split(',')
                    """
                    3 == 3
                    """
                    print("Equation : ")
                    print(tmp_list)
                    for item_x in range(0, len(tmp_list) - 1, 2):
                        if tmp_list[item_x] == 'const':
                            tmp_list[item_x] = equ_normal[item_x]
                        else:
                            c_id = int(tmp_list[item_x])
                            print("C_id : " + str(c_id))
                            val = Basedetails.objects.filter(Q(bc_fk=c_id) & Q(row_num=row_no)).values('pk', 'c_v')
                            if len(list(val)) != 0:
                                print("Val : ")
                                print(val)
                                tmp_list[item_x] = val[0]['c_v']
                            else:
                                tmp_list[item_x] = 0

                    print("###### Formted equation : ######")
                    print(tmp_list)
                    if item['type_of_calc'] == 'Date_With_Const':
                        if data[0]['const_position'] == 1:
                            print("DATE CALCILATION WITH CONST POSITION 1")
                            x1 = tmp_list[0]
                            x2 = tmp_list[2]
                            op = tmp_list[1]
                            result = days_betwenn_constant(x1, x2, op)
                            print("1st Time result : " + str(result))
                            for y in range(3, len(tmp_list) - 1, 2):
                                op = tmp_list[y]
                                x2 = tmp_list[y + 1]
                                result = days_betwenn_constant(result, x2, op)
                                print("Result : " + str(result))
                            Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(
                                c_v=result)
                            rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).\
                                values('pk', 'c_v')
                            print("Rs :")
                            print(rs)
                            rs_pk.append(rs[0]['pk'])
                            rs_val.append(rs[0]['c_v'])
                            print("Final Result : " + str(result))
                        else:
                            print("DATE CALCULATION WITH CONST POSITION 2")
                            x1 = tmp_list[0]
                            x2 = tmp_list[2]
                            op = tmp_list[1]
                            print("x1 : " + str(x1))
                            print("x2 : " + str(x2))
                            result = days_betwenn_constant(x1, x2, op)
                            print("1st Time result : " + str(result))
                            for y in range(3, len(tmp_list) - 1, 2):
                                op = tmp_list[y]
                                x2 = tmp_list[y + 1]
                                result = days_betwenn_constant(result, x2, op)
                            print("Result : " + str(result))
                            print("fk column : " + str(item['fk_column']))
                            if Basedetails.objects.filter(bc_fk=item['fk_column']).count() > 0:
                                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                                Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                                rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).values('pk', 'c_v')
                            print("Rs :")
                            print(rs)
                            rs_pk.append(rs[0]['pk'])
                            rs_val.append(rs[0]['c_v'])
                            print("Final Result : " + str(result))
                    elif item['type_of_calc'] == 'Date_Calc':
                        print("DATE CALCULATION NORMAL")
                        x1 = tmp_list[0]
                        x2 = tmp_list[2]
                        op = tmp_list[1]
                        print("x1 : " + str(x1) + "op : " + str(op) + "x2 : " + str(x2))
                        result = days_between(x1, x2, op)
                        print("1st Time result : " + str(result))
                        for y in range(3, len(tmp_list) - 1, 2):
                            op = tmp_list[y]
                            x2 = tmp_list[y + 1]
                            result = days_between(result, x2, op)
                            print("Result : " + str(result))

                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).\
                            values('pk', 'c_v')
                        print("Rs :")
                        print(rs)
                        rs_pk.append(rs[0]['pk'])
                        rs_val.append(rs[0]['c_v'])
                        print("Final Result : " + str(result))
                    else:
                        print('NORMAL CALCULATION')
                        x1 = tmp_list[0]
                        x2 = tmp_list[2]
                        op = tmp_list[1]

                        result = operation(x1, x2, op)
                        print("1st Time result : " + str(result))
                        for y in range(3, len(tmp_list) - 1, 2):
                            op = tmp_list[y]
                            x2 = tmp_list[y + 1]
                            result = operation(result, x2, op)
                            print("Result : " + str(result))
                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).\
                            values('pk', 'c_v')
                        print("Rs :")
                        print(rs)
                        rs_pk.append(rs[0]['pk'])
                        rs_val.append(rs[0]['c_v'])
                        print("Final Result : " + str(result))

            return JsonResponse({'dataresult': 'Inline Value Upadated', 'rs_pk': rs_pk, 'rs_val': rs_val})
        except Exception as e:
            return HttpResponse(e)


def delete_row(request):
    """
    param:m_d :- ID of value
    param:table_id :- ID of Table
    """
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            m_id = request.POST['id']
            table_id = request.POST['base_id']

            print("m_id : " + m_id)

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()
            orginal_val = Basedetails.objects.get(pk=m_id)
            orginal_val = orginal_val.c_v
            print("************************************")
            print("Origanal Value : " + orginal_val)
            if data == 1:
                print("Row Delete Option menu")
                primary_list = []
                table_prime = []
                ck = True
                check_id = table_id
                while(ck):
                    tmp_data = Basecolumns.objects.filter(d_type=check_id).values('pk', 'd_type', 'base_fk')
                    numeric_check = False
                    for x in tmp_data:
                        if x['d_type'].isnumeric():
                            numeric_check = True
                            primary_list.append(x['pk'])
                            table_prime.append(x['base_fk'])
                            check_id = x['base_fk']
                    if not numeric_check:
                        ck = False
                print("primary list ->")
                print(primary_list)
                print("table_prime -->")
                print(table_prime)
                deletin_id = [orginal_val]
                for x in range(0, len(primary_list)):
                    print("******************")
                    tmp_get_data = Basecolumns.objects.filter(base_fk=table_prime[x]).values('pk')
                    print(tmp_get_data)
                    for y in tmp_get_data:
                        if Basedetails.objects.filter(Q(bc_fk=y['pk']) & Q(c_v__in=deletin_id)).count() > 0:
                            print("&&&&&&&&&&&&&&")
                            rt = Basedetails.objects.filter(Q(bc_fk=y['pk']) & Q(c_v__in=deletin_id)).values('row_num')
                            print("RT : ")
                            print(rt)
                            for m in rt:
                                dl_ids = Basedetails.objects.filter(Q(bc_fk__in=tmp_get_data) & Q(row_num=m['row_num'])).values('pk', 'c_v')
                                print("Deleted ids : ")
                                print(dl_ids)
                                for k in dl_ids:
                                    deletin_id.append(k['c_v'])
                                Basedetails.objects.filter(Q(bc_fk__in=tmp_get_data) & Q(row_num=m['row_num'])).delete()
                        else:
                            print("###########")
                Basedetails.objects.filter(pk=m_id).delete()
                return HttpResponse('Root User Deleted Record')
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('delete_data')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['delete_data'] == 'true':
                        print("Row Delete Option menu")
                        primary_list = []
                        table_prime = []
                        ck = True
                        check_id = table_id
                        while (ck):
                            tmp_data = Basecolumns.objects.filter(d_type=check_id).values('pk', 'd_type', 'base_fk')
                            numeric_check = False
                            for x in tmp_data:
                                if x['d_type'].isnumeric():
                                    numeric_check = True
                                    primary_list.append(x['pk'])
                                    table_prime.append(x['base_fk'])
                                    check_id = x['base_fk']
                            if not numeric_check:
                                ck = False
                        print("primary list ->")
                        print(primary_list)
                        print("table_prime -->")
                        print(table_prime)
                        deletin_id = [orginal_val]
                        for x in range(0, len(primary_list)):
                            print("******************")
                            tmp_get_data = Basecolumns.objects.filter(base_fk=table_prime[x]).values('pk')
                            print(tmp_get_data)
                            for y in tmp_get_data:
                                if Basedetails.objects.filter(Q(bc_fk=y['pk']) & Q(c_v__in=deletin_id)).count() > 0:
                                    print("&&&&&&&&&&&&&&")
                                    rt = Basedetails.objects.filter(Q(bc_fk=y['pk']) & Q(c_v__in=deletin_id)).values(
                                        'row_num')
                                    print("RT : ")
                                    print(rt)
                                    for m in rt:
                                        dl_ids = Basedetails.objects.filter(
                                            Q(bc_fk__in=tmp_get_data) & Q(row_num=m['row_num'])).values('pk', 'c_v')
                                        print("Deleted ids : ")
                                        print(dl_ids)
                                        for k in dl_ids:
                                            deletin_id.append(k['c_v'])
                                        Basedetails.objects.filter(
                                            Q(bc_fk__in=tmp_get_data) & Q(row_num=m['row_num'])).delete()
                                else:
                                    print("###########")
                        Basedetails.objects.filter(pk=m_id).delete()

                        print("Notification Sending......")
                        notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)) \
                            .values('user_id')
                        msg = str(login_user) + ' Deleted a  Record From ' + str(table_real_name)
                        for x in notfy:
                            if x['user_id'] != login_user:
                                notification_sender(sender_id=request.session['user_id'],
                                                    user_email=x['user_id'], status=1,
                                                    heading="Deleted a Record", message=msg)
                        # SENDING TO TABLE OWNER
                        notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                            status=1, heading="Deleted a Record", message=msg)
                        return JsonResponse({'Result': 'Non Root User Deleted a Record'})
            else:
                messages.success(request, 'User have no permission for Delete Record')
                return JsonResponse({'Result': 'User have no permission for Delete Record'})

        except Exception as e:
            return HttpResponse(e)


# RENAMING COLUMN
def edit_column(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            table_id = request.POST['base_id']
            # COLUMN ID
            c_id = request.POST['id']
            # NEW NAME OF COLUMN
            c_val = request.POST['val']

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()
            if data == 1:
                Basecolumns.objects.filter(pk=c_id).update(c_name=c_val)
                tmp_calc_data = Calculation.objects.all()
                for k in tmp_calc_data:
                    split_list_equ_normal = str(k.equ_normal).split(',')
                    split_list_equ = str(k.equ).split(',')
                    final_result_column = ""
                    for y in range(0, len(split_list_equ)-1):
                        print(split_list_equ[y])
                        if split_list_equ[y] == c_id:
                            final_result_column = final_result_column + c_val + ","
                            print("*****************")
                        else:
                            final_result_column = final_result_column + split_list_equ_normal[y] + ","
                            print("&&&&&&&&&&&&&&&")
                        print(final_result_column)
                    Calculation.objects.filter(pk=k.pk).update(equ_normal=final_result_column)

                return JsonResponse({'Result': 'Root User Updated Column Name'})
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('update_col')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['update_col'] == 'true':
                        Basecolumns.objects.filter(pk=c_id).update(c_name=c_val)
                        print("Notification Sending......")
                        notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)) \
                            .values('user_id')
                        msg = str(login_user) + ' Column Name Updated In ' + str(table_real_name)
                        for x in notfy:
                            if x['user_id'] != login_user:
                                notification_sender(sender_id=request.session['user_id'],
                                                    user_email=x['user_id'], status=1,
                                                    heading="Deleted Filed", message=msg)
                        # SENDING TO TABLE OWNER
                        notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                            status=1, heading="Column Name Updated", message=msg)
                        return JsonResponse({'Result': 'Non Root User Renamed Column Name'})
            else:
                messages.success(request, 'User have no permission for Rename column')
                return JsonResponse({'Result': 'User have no permission for Rename column'})

        except Exception as e:
            return HttpResponse(e)

# COLUMN DELETION PROCESS
def Columndelete(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email
            table_id = request.POST['base_id']
            del_id = request.POST['id']
            col_id = Basecolumns.objects.get(id=del_id)

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()
            # Checking table is created by Root User
            if data == 1:
                # If it is calculation Column
                if Calculation.objects.filter(fk_column=del_id).count() > 0:
                    Basedetails.objects.filter(bc_fk=col_id).delete()
                    Basecolumns.objects.filter(id=del_id).delete()
                    Calculation.objects.filter(fk_column=del_id).delete()
                    print("The Column is Calcluation column so direct delete possible")
                    return JsonResponse({'Result': 'Root User Deleted Table', 'status': True})
                # Not a Calculation column Checking possible calculation equations
                else:
                    calc_tbl_data = Calculation.objects.all()

                    for x in calc_tbl_data:
                        print("Insede loop 1")
                        # Split equation and equation column id
                        equation_list = str(x.equ_normal).split(',')
                        equation_ids = str(x.equ).split(',')
                        equation_availabilty =  False
                        # Checking the column present is equation
                        if del_id in equation_ids:
                            equation_availabilty = True
                            print(" equation_list : ")
                            print(equation_list)
                            print("equation_ids" )
                            print(equation_ids)
                            final_result_column = ""
                            final_result_id = ""
                            count = 0
                            # Removing column from equation
                            for y in range(0, len(equation_ids) - 1, 2):
                                print("inside Loop 2")
                                if equation_ids[y] != str(del_id):
                                    if y+1 < len(equation_ids) - 2:
                                        final_result_column = final_result_column + equation_list[y] + ',' + equation_list[y + 1] + ','
                                        final_result_id = final_result_id + equation_ids[y] + ',' + equation_ids[y + 1] + ','
                                        count = count + 1
                                    else:
                                        final_result_column = final_result_column + equation_list[y]
                                        final_result_id = final_result_id + equation_ids[y]
                                        count = count + 1
                            # Final Result of equation should not be empty
                            if final_result_id != "" and final_result_column != "":
                                print("#######################################")
                                print("Final result Column :")
                                print(final_result_column)
                                print("Final result Column Id :")
                                print(final_result_id)

                                check_list = ['+', '-', '*', '/']
                                # removing addition characters from equation
                                if final_result_column[-2] in check_list and final_result_column[-1] == ',':
                                    final_result_column = final_result_column[:-2]
                                    final_result_id = final_result_id[:-2]

                            print("*************************************")
                            # Adding addition coma to equation if not present in new equation
                            if final_result_column[-1] != ',':
                                final_result_column = final_result_column + ','
                                final_result_id= final_result_id + ','

                            print("Final result Column :")
                            print(final_result_column)
                            print("Final result Column Id :")
                            print(final_result_id)
                            print("PK : " + str(x.pk))
                            print("Fk Colum : " + str(x.fk_column))
                            print("count : " + str(count))
                            # Checking number of columns in new equation if it less than or equal to 1 deletion not possible
                            if count > 1:
                                Calculation.objects.filter(pk=x.pk).update(equ_normal=final_result_column,
                                                                           equ=final_result_id)
                                calc_genaral_update(calc_id=x.pk, column_id=x.fk_column)
                                Basedetails.objects.filter(bc_fk=col_id).delete()
                                Basecolumns.objects.filter(id=del_id).delete()
                                return JsonResponse({'Result': 'Root User Deleted Table', 'data': final_result_column,
                                                     'status': True})
                            else:
                                print("Not able to delete")
                                return JsonResponse({'Result': 'Equation is not good enough to perform this operation',
                                                     'status': False})
                    # It's Not a Calculation column and not part of any equation it is a normal column
                    if not equation_availabilty:
                        print("Its Not a Calculation column and not part of any equation")
                        Basedetails.objects.filter(bc_fk=col_id).delete()
                        Basecolumns.objects.filter(id=del_id).delete()
                        return JsonResponse({'Result': 'Root User Deleted Table', 'status': True})
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('delete_col')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['delete_col'] == 'true':
                        print("Notification Sending......")
                        notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)) \
                            .values('user_id')
                        msg = str(login_user) + ' Deleted  Field From ' + str(table_real_name)
                        for x in notfy:
                            if x['user_id'] != login_user:
                                notification_sender(sender_id=request.session['user_id'],
                                                    user_email=x['user_id'], status=1,
                                                    heading="Deleted Filed", message=msg)
                        # SENDING TO TABLE OWNER
                        notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                            status=1, heading="Deleted Filed", message=msg)

                        if Calculation.objects.filter(fk_column=del_id).count() > 0:
                            # Basedetails.objects.filter(bc_fk=col_id).delete()
                            # Basecolumns.objects.filter(id=del_id).delete()
                            # Calculation.objects.filter(fk_column=del_id).delete()
                            print("The Column is Calcluation column so direct delete possible")
                            return JsonResponse({'Result': 'Non Root User Deleted Table', 'status': True})
                        else:
                            calc_tbl_data = Calculation.objects.all()

                            for x in calc_tbl_data:
                                print("Inside loop 1")
                                equation_list = str(x.equ_normal).split(',')
                                equation_ids = str(x.equ).split(',')
                                if del_id in equation_ids:
                                    print(" equation_list : ")
                                    print(equation_list)
                                    print("equation_ids")
                                    print(equation_ids)
                                    final_result_column = ""
                                    final_result_id = ""

                                    for y in range(0, len(equation_ids) - 1, 2):
                                        print("inside Loop 2")
                                        print(y)
                                        if equation_ids[y] != str(del_id):
                                            if y + 1 < len(equation_ids) - 2:
                                                final_result_column = final_result_column + equation_list[y] + ',' + \
                                                                      equation_list[y + 1] + ','
                                                final_result_id = final_result_id + equation_ids[y] + ',' + \
                                                                  equation_ids[y + 1] + ','
                                            else:
                                                final_result_column = final_result_column + equation_list[y]
                                                final_result_id = final_result_id + equation_ids[y]

                                    if final_result_id != "" and final_result_column != "":
                                        print("#######################################")
                                        print("Final result Column :")
                                        print(final_result_column)
                                        print("Final result Column Id :")
                                        print(final_result_id)

                                        check_list = ['+', '-', '*', '/']

                                        if final_result_column[-2] in check_list and final_result_column[-1] == ',':
                                            final_result_column = final_result_column[:-2]
                                            final_result_id = final_result_id[:-2]

                                    print("*************************************")
                                    # print(len(equation_ids) - 1)

                                    final_result_column = final_result_column + ','
                                    final_result_id = final_result_id + ','

                                    print("Final result Column :")
                                    print(final_result_column)
                                    print("Final result Column Id :")
                                    print(final_result_id)
                                    print("PK : " + str(x.pk))
                                    print("Fk Colum : " + str(x.fk_column))
                                    if len(final_result_column.split(',')) < 1:
                                        Calculation.objects.filter(pk=x.pk).update(equ_normal=final_result_column,
                                                                                   equ=final_result_id)
                                        calc_genaral_update(calc_id=x.pk, column_id=x.fk_column)
                                        # Basedetails.objects.filter(bc_fk=col_id).delete()
                                        # Basecolumns.objects.filter(id=del_id).delete()
                                        return JsonResponse({'Result': 'Non Root User Deleted Table',  'status': True})
                                    else:
                                        print("Not able to delete")
                                        return JsonResponse(
                                            {'Result': 'Equation is not good enough to perform this operation',
                                             'status': False})
            else:
                messages.success(request, 'User have no permission for Delete column')
                return JsonResponse({'Result': 'User have no permission for Delete column'})
        except Exception as e:
            return HttpResponse(e)



def calc_genaral_update(calc_id, column_id):
    base_data = Basedetails.objects.filter(bc_fk=column_id).values('row_num')
    print("*** Base Data ***")
    print(base_data)
    for map in base_data:
        row_no = map['row_num']
        rs_pk = []
        rs_val = []

        data = Calculation.objects.filter(pk=calc_id).values('equ', 'fk_column', 'equ_normal',
                                                             'type_of_calc', 'const_position')
        print("Calc data : ")
        print(data)
        data_tmp = list(data)
        for item in data_tmp:
            tmp_list = str(item['equ']).split(',')
            print("tmp_list : ")
            print(tmp_list)
            equ_normal = str(item['equ_normal']).split(',')
            print("equ_normal : ")
            print(equ_normal)
            for item_x in range(0, len(tmp_list) - 1, 2):
                if tmp_list[item_x] == 'const':
                    tmp_list[item_x] = equ_normal[item_x]
                else:
                    c_id = int(tmp_list[item_x])
                    val = Basedetails.objects.filter(Q(bc_fk=c_id) & Q(row_num=row_no)).values('pk', 'c_v')
                    if len(list(val)) != 0:
                        tmp_list[item_x] = val[0]['c_v']
                    else:
                        tmp_list[item_x] = 0
            if item['type_of_calc'] == 'Date_With_Const':
                if data[0]['const_position'] == 1:
                    print("DATE CALCILATION WITH CONST POSITION 1")
                    x1 = tmp_list[0]
                    x2 = tmp_list[2]
                    op = tmp_list[1]
                    result = days_betwenn_constant(x1, x2, op)
                    print("1st Time result : " + str(result))
                    for y in range(3, len(tmp_list) - 1, 2):
                        op = tmp_list[y]
                        x2 = tmp_list[y + 1]
                        result = days_betwenn_constant(result, x2, op)
                        print("Result : " + str(result))
                    Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                    rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).values('pk', 'c_v')
                    print("Rs :")
                    print(rs)
                    rs_pk.append(rs[0]['pk'])
                    rs_val.append(rs[0]['c_v'])
                    print("Final Result : " + str(result))
                else:
                    print("DATE CALCULATION WITH CONST POSITION 2")
                    x1 = tmp_list[0]
                    x2 = tmp_list[2]
                    op = tmp_list[1]
                    print("x1 : " + str(x1))
                    print("x2 : " + str(x2))
                    result = days_betwenn_constant(x1, x2, op)
                    print("1st Time result : " + str(result))
                    for y in range(3, len(tmp_list) - 1, 2):
                        op = tmp_list[y]
                        x2 = tmp_list[y + 1]
                        result = days_betwenn_constant(result, x2, op)
                    print("Result : " + str(result))
                    print("fk column : " + str(item['fk_column']))
                    if Basedetails.objects.filter(bc_fk=item['fk_column']).count() > 0:
                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).values('pk', 'c_v')
                    rs_pk.append(rs[0]['pk'])
                    rs_val.append(rs[0]['c_v'])
                    print("Final Result : " + str(result))
            elif item['type_of_calc'] == 'Date_Calc':
                print("DATE CALCULATION NORMAL")
                x1 = tmp_list[0]
                x2 = tmp_list[2]
                op = tmp_list[1]
                print("x1 : " + str(x1) + "op : " + str(op) + "x2 : " + str(x2))
                result = days_between(x1, x2, op)
                print("1st Time result : " + str(result))
                for y in range(3, len(tmp_list) - 1, 2):
                    op = tmp_list[y]
                    x2 = tmp_list[y + 1]
                    result = days_between(result, x2, op)
                    print("Result : " + str(result))

                Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                    values('pk', 'c_v')
                rs_pk.append(rs[0]['pk'])
                rs_val.append(rs[0]['c_v'])
                print("Final Result : " + str(result))
            else:
                print('NORMAL CALCULATION')
                print(tmp_list)
                x1 = tmp_list[0]
                x2 = tmp_list[2]
                op = tmp_list[1]

                result = operation(x1, x2, op)
                print("1st Time result : " + str(result))
                for y in range(3, len(tmp_list) - 1, 2):
                    op = tmp_list[y]
                    x2 = tmp_list[y + 1]
                    result = operation(result, x2, op)
                    print("Result : " + str(result))
                Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).values('pk', 'c_v')
                rs_pk.append(rs[0]['pk'])
                rs_val.append(rs[0]['c_v'])
                print("Final Result : " + str(result))


# DROP TABLEAND RELATED COLUMNS AND DATA
def Deletebase(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email
            table_id = request.POST['id']

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            c = []
            # FILTERING ALL THE COLUMNS RELATED TO THAT TABLE
            columns = Basecolumns.objects.filter(base_fk=table_id).values('pk')
            for item in columns:
                c.append(item['pk'])

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()

            if data == 1:
                if Basecolumns.objects.filter(d_type=table_id).count()>0:
                    messages.success(request,'Record under transaction so '
                                         'not possible to delete the Table')

                    return

                else:


                    # REMOVING DATA RELATED TO COLUMNS
                    Basedetails.objects.filter(bc_fk__in=c).delete()
                    # REMOVING COLUMNS RELATED TO TABLE
                    Basecolumns.objects.filter(base_fk=table_id).delete()
                    # REMOVING REPORTS RELATED TO TABLE
                    Report.objects.filter(table_id=table_id).delete()
                    # REMOVING TABLE

                    if Group_model_primary.objects.filter(table_id_primary=table_id).count() > 0:
                        primary_data = Group_model_primary.objects.filter(table_id_primary=table_id).values('pk')
                        tgp = []
                        for k in primary_data:
                            tgp.append(k['pk'])
                        Group_model_secondary.objects.filter(primary_table_fk__in=tgp).delete()
                        Group_model_primary.objects.filter(pk__in=tgp).delete()


                    else:
                        Group_model_secondary.objects.filter(secondary_tables_id=table_id).delete()


                    Base.objects.get(pk=table_id).delete()
                    return JsonResponse({'Result': 'Root User Deleted Table'})
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('create_tables')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['create_tables'] == 'true':
                        if Basecolumns.objects.filter(d_type=table_id).count()>0:
                            messages.success(request,'Record under transaction so '
                                                'not possible to delete the Table')

                            return
                        else:
                            # REMOVING DATA RELATED TO COLUMNS
                            Basedetails.objects.filter(bc_fk__in=c).delete()
                            # REMOVING COLUMNS RELATED TO TABLE
                            Basecolumns.objects.filter(base_fk=table_id).delete()
                            # REMOVING REPORTS RELATED TO TABLE
                            Report.objects.filter(table_id=table_id).delete()
                            # REMOVING TABLE

                            if Group_model_primary.objects.filter(table_id_primary=table_id).count() > 0:
                                primary_data = Group_model_primary.objects.filter(table_id_primary=table_id).values('pk')
                                tgp = []
                                for k in primary_data:
                                    tgp.append(k['pk'])


                                Group_model_secondary.objects.filter(primary_table_fk__in=tgp).delete()
                                Group_model_primary.objects.filter(pk__in=tgp).delete()
                            else:
                                Group_model_secondary.objects.filter(secondary_tables_id=table_id).delete()

                            Base.objects.get(pk=table_id).delete()

                        print("Notification Sending......")
                        notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)) \
                            .values('user_id')
                        msg = str(login_user) + 'Deleted Table' + str(table_real_name)
                        for x in notfy:
                            if x['user_id'] != login_user:
                                notification_sender(sender_id=request.session['user_id'],
                                                    user_email=x['user_id'], status=1,
                                                    heading="Deleted Table", message=msg)
                        # SENDING TO TABLE OWNER
                        notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                            status=1, heading="Deleted Table", message=msg)
                        return JsonResponse({'Result': 'Non Root User Deleted Table'})
            else:
                messages.success(request, 'User have no permission for Delete Table')
                return JsonResponse({'Result': 'User have no permission for Delete Table'})
        except Exception as e:
            return HttpResponse(e)

def Deletebasedetails(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            table_id = request.POST['id']

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            b = []
            base_columns = Basecolumns.objects.filter(base_fk=table_id).values('pk')
            for item in base_columns:
                b.append(item['pk'])

            data = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()

            if data == 1:
                # REMOVING DATA RELATED TO COLUMNS
                Basedetails.objects.filter(bc_fk__in=b).delete()
                return JsonResponse({'Result': 'Root User Deleted All The Data'})
            elif data != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('create_tables')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['create_tables'] == 'true':
                        print("Notification Sending......")
                        notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)) \
                            .values('user_id')
                        msg = str(login_user) + 'Deleted All Records Form ' + str(table_real_name)
                        for x in notfy:
                            if x['user_id'] != login_user:
                                notification_sender(sender_id=request.session['user_id'],
                                                    user_email=x['user_id'], status=1,
                                                    heading="All Record Deleted", message=msg)
                        # SENDING TO TABLE OWNER
                        notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                            status=1, heading="All Record Deleted", message=msg)
                        return JsonResponse({'Result': 'Non Root User Deleted All Data'})
            else:
                messages.success(request, "You don't have permission")
                return JsonResponse({'Result': "You don't have permission"})
        except Exception as e:
            return HttpResponse(e)


def infoedit(request):
    try:
        if request.method == "POST":
            basedata = Base.objects.get(id=request.POST['id'])
            update = 0
            if basedata.base_name != request.POST['bname']:
                basedata.base_name = request.POST['bname']
                update += 1

            if basedata.technical_name != request.POST['tname']:
                basedata.technical_name = request.POST['tname']
                update += 1
            if basedata.table_type != request.POST['ttype']:
                basedata.table_type = request.POST['ttype']
                update += 1
            if basedata.discription != request.POST['desc']:
                basedata.discription = request.POST['desc']
                update += 1
            if basedata.purpose != request.POST['purp']:
                basedata.purpose = request.POST['purp']
                update += 1
            if basedata.bcp != request.POST['bcp']:
                basedata.bcp = request.POST['bcp']
                update += 1
            if basedata.tags != request.POST['tag']:
                basedata.tags = request.POST['tag']
                update += 1
            if update > 0:
                basedata.save()
        return JsonResponse({'data': 'updated'})

    except Exception as e:
        print(e)
        return HttpResponse(e)


def Updatepassword(request):
    try:
        if request.method == "POST":
            user = Login.objects.get(id=request.session['user_id'])
            print(user)
            cpass = request.POST['cpass']
            print(cpass)
            npass = request.POST['npass']
            if user.password == cpass :
                update = 0
                if user.password != npass :
                    user.password = npass
                    update += 1
                    if update > 0:
                        user.save()
                        messages.success(request, 'New password Updated')
                else:
                    messages.success(request, 'New password same as old Password')
            else:
                messages.success(request, 'Current password not same')
        return HttpResponseRedirect('/userprofile')
    except Exception as e:
        print(e)
        return HttpResponse(e)


def userprofile(request):
    if request.method == "POST":
        user_in = Login.objects.get(id=request.session['user_id'])
        user_email = user_in.email
        account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
        login_obj = Login.objects.all().exclude(id=request.session['user_id'])
        pro = Profile.objects.filter(log_fk=request.session['user_id'])
        designations=designation.objects.all()
        # Profile pic avilable or not
        profile_pic = ''
        if len(list(pro)) !=0:
            if pro[0].user_image == None:
                profile_pic = 'media/user.jpg'
            else:
                profile_pic = pro[0].user_image.url
        else:
            profile_pic = 'media/user.jpg'
        sub_tbl = Group_model_secondary.objects.all()
        tmp_menu_pk = []
        for item in sub_tbl:
            tmp_menu_pk.append(item.secondary_tables_id)
        menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                data_count = Profile.objects.filter(log_fk=request.session['user_id']).count()
                if data_count == 0:
                    section = form.save(commit=False)
                    section.log_fk = request.session['user_id']
                    section.save()
                    return render(request, 'userdetails.html', {'form': form, 'menus': menus,'profile_pic': profile_pic,
                                                                'account_details':account_details,'login_obj':login_obj,
                                                                'designations':designations})
                else:
                    pro = Profile.objects.get(log_fk=request.session['user_id'])
                    form_up = ProfileForm(request.POST, request.FILES, instance = pro)
                    form_up.save()
                    return render(request, 'userdetails.html', {'form': form, 'pro': pro, 'menus': menus,
                                                                'user': user_in,'profile_pic': profile_pic,
                                                                'account_details':account_details,'login_obj':login_obj,
                                                                'designations':designations})
            except Exception as e:
                return HttpResponse(e)
        else:
            pass
            # return HttpResponse(form)
    else:
        user_in = Login.objects.get(id=request.session['user_id'])
        user_email = user_in.email
        account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
        login_obj = Login.objects.all().exclude(id=request.session['user_id'])
        pro = Profile.objects.filter(log_fk=request.session['user_id'])
        designations=designation.objects.all()
        # Profile pic avilable or not
        profile_pic = ''
        if len(list(pro)) !=0:
            if pro[0].user_image == None:
                profile_pic = 'media/user.jpg'
            else:
                profile_pic = pro[0].user_image.url
        else:
            profile_pic = 'media/user.jpg'
        sub_tbl = Group_model_secondary.objects.all()
        tmp_menu_pk = []
        for item in sub_tbl:
            tmp_menu_pk.append(item.secondary_tables_id)
        menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

        data_count = Profile.objects.filter(log_fk=request.session['user_id']).count()
        if data_count > 0:
            pro = Profile.objects.get(log_fk=request.session['user_id'])
            form = ProfileForm(instance=pro)
            return render(request, 'userdetails.html', {'form': form, 'pro': pro, 'menus': menus, 'user': user_in,'profile_pic': profile_pic,
                                                        'account_details':account_details,'login_obj':login_obj,'designations':designations})
        else:
            form = ProfileForm()
            return render(request, 'userdetails.html', {'form': form, 'menus': menus, 'user': user_in,'profile_pic': profile_pic,
                                                        'account_details':account_details,'login_obj':login_obj,'designations':designations})


def calculation_page(request):
    try:
        if request.session.has_key('user_id'):
            user_in = Login.objects.get(id=request.session['user_id'])
            user_email = user_in.email
            pkp = request.POST['pkp']
            # Fetching the columns related to master table
            t = ['String', 'Text', 'Image', 'Time']
            alls = Basecolumns.objects.filter(Q(base_fk=pkp) & ~Q(d_type__in=t)).values('base_name', 'c_name',
                                                                                        'base_fk', 'pk', 'd_type')
            tmp = []
            for item in alls:
                if item['d_type'].isnumeric():
                    data = Basecolumns.objects.filter(Q(base_fk=item['d_type']) & Q(c_name=item['c_name'])).\
                        values('base_name', 'c_name', 'base_fk', 'pk', 'd_type')
                    for x in data:
                        if x['d_type'] not in t:
                            print(data)
                            tmp.append(item['pk'])
                else:
                    tmp.append(item['pk'])
            print("============= CALCULATION TMP ARRAY ===============")
            print(tmp)
            alls = Basecolumns.objects.filter(pk__in=tmp).values('base_name', 'c_name', 'base_fk', 'pk', 'd_type')
            final_calc_columns = []
            all_calc = Calculation.objects.filter(fk_table=pkp).values('pk', 'fk_column', 'equ_normal')
            for item in all_calc:
                if Basecolumns.objects.filter(id=item['fk_column']).count() > 0:
                    bk = Basecolumns.objects.get(id=item['fk_column'])
                    dic = {'column_id': item['fk_column'], 'column_name': bk.c_name, 'calc_id':item['pk'],
                           'equ': item['equ_normal']}
                    final_calc_columns.append(dic)
            return JsonResponse({'Result': list(alls), 'Calc': final_calc_columns})
        else:
            return HttpResponseRedirect('/login')
    except Exception as e:
        return HttpResponse(e)


def calc_equation_fetch(request):
    if request.method == 'POST':
        try:
            col_fk = request.POST['col_fk']
            bk_column = Basecolumns.objects.get(id=col_fk)
            bk_calc = Calculation.objects.get(fk_column=col_fk)
            return JsonResponse({'col_name': bk_column.c_name, 'calc_id': bk_calc.pk,
                                 'calc_equ': bk_calc.equ_normal.replace(',', '')})
        except Exception as e:
            return HttpResponse(e)


def calc_edit(request):
    if request.method == 'POST':
        try:
            # ARRAY WITH COLUMN NAME
            vals = request.POST.getlist('calc_val[]')
            # ARRAY WITH ORIGINAL COLUMN NAME
            original_vals = request.POST.getlist('calc_val_original[]')
            # ARRAY WITH COLUMN IDS
            ids = request.POST.getlist('calc_id[]')

            original_column_name = request.POST['original_col_name']
            result_name = request.POST['rs_column']
            column_id = request.POST['column_id']
            calc_id = request.POST['calc_pk']
            table_id = request.POST['base_id']

            base_data = Basedetails.objects.filter(bc_fk=column_id).values('row_num')

            str_ids = ""
            str_vals = ""

            for item in vals:
                str_vals = str_vals + item + ','
            for item in ids:
                str_ids = str_ids + item + ','
            for map in base_data:
                row_no = map['row_num']
                rs_pk = []
                rs_val = []
                Calculation.objects.filter(pk=calc_id).update(equ=str_ids, equ_normal=str_vals)
                if result_name != "":
                    Basecolumns.objects.filter(pk=column_id).update(c_name=result_name)
                else:
                    Basecolumns.objects.filter(pk=column_id).update(c_name=original_column_name)

                """
                   # id	equ	fk_table	fk_column	createdby	equ_normal
                   1	3,+,2,	1	20	jitheeshemmanuel@gmail.com	Maths,+,Science,
                   2	2,-,20,	1	21	jitheeshemmanuel@gmail.com	Science,-,SUM,
                """
                data = Calculation.objects.filter(pk=calc_id).values('equ', 'fk_column', 'equ_normal',
                                                                            'type_of_calc', 'const_position')
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                print(data)
                data_tmp = list(data)
                for item in data_tmp:
                    """
                    1---> [   3   +   2   '']
                    2---> [   2   -   20  '']
                    """
                    tmp_list = str(item['equ']).split(',')
                    equ_normal = str(item['equ_normal']).split(',')
                    """
                    3 == 3
                    """
                    print("Equation : ")
                    print(tmp_list)
                    for item_x in range(0, len(tmp_list) - 1, 2):
                        print(item_x)
                        if tmp_list[item_x] == 'const':
                            tmp_list[item_x] = equ_normal[item_x]
                        else:
                            c_id = int(tmp_list[item_x])
                            print("C_id : " + str(c_id))
                            val = Basedetails.objects.filter(Q(bc_fk=c_id) & Q(row_num=row_no)).values('pk', 'c_v')
                            if len(list(val)) != 0:
                                print("Val : ")
                                print(val)
                                tmp_list[item_x] = val[0]['c_v']
                                print("###################################")
                            else:
                                tmp_list[item_x] = 0

                    print("###### Formted equation : ######")
                    print(tmp_list)
                    if item['type_of_calc'] == 'Date_With_Const':
                        if data[0]['const_position'] == 1:
                            print("DATE CALCILATION WITH CONST POSITION 1")
                            x1 = tmp_list[0]
                            x2 = tmp_list[2]
                            op = tmp_list[1]
                            result = days_betwenn_constant(x1, x2, op)
                            print("1st Time result : " + str(result))
                            for y in range(3, len(tmp_list) - 1, 2):
                                op = tmp_list[y]
                                x2 = tmp_list[y + 1]
                                result = days_betwenn_constant(result, x2, op)
                                print("Result : " + str(result))
                            Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(
                                c_v=result)
                            rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                                values('pk', 'c_v')
                            print("Rs :")
                            print(rs)
                            rs_pk.append(rs[0]['pk'])
                            rs_val.append(rs[0]['c_v'])
                            print("Final Result : " + str(result))
                        else:
                            print("DATE CALCULATION WITH CONST POSITION 2")
                            x1 = tmp_list[0]
                            x2 = tmp_list[2]
                            op = tmp_list[1]
                            print("x1 : " + str(x1))
                            print("x2 : " + str(x2))
                            result = days_betwenn_constant(x1, x2, op)
                            print("1st Time result : " + str(result))
                            for y in range(3, len(tmp_list) - 1, 2):
                                op = tmp_list[y]
                                x2 = tmp_list[y + 1]
                                result = days_betwenn_constant(result, x2, op)
                            print("Result : " + str(result))
                            print("fk column : " + str(item['fk_column']))
                            if Basedetails.objects.filter(bc_fk=item['fk_column']).count() > 0:
                                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                                Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(
                                    c_v=result)
                                rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).values('pk',
                                                                                                                       'c_v')
                            print("Rs :")
                            print(rs)
                            rs_pk.append(rs[0]['pk'])
                            rs_val.append(rs[0]['c_v'])
                            print("Final Result : " + str(result))
                    elif item['type_of_calc'] == 'Date_Calc':
                        print("DATE CALCULATION NORMAL")
                        x1 = tmp_list[0]
                        x2 = tmp_list[2]
                        op = tmp_list[1]
                        print("x1 : " + str(x1) + "op : " + str(op) + "x2 : " + str(x2))
                        result = days_between(x1, x2, op)
                        print("1st Time result : " + str(result))
                        for y in range(3, len(tmp_list) - 1, 2):
                            op = tmp_list[y]
                            x2 = tmp_list[y + 1]
                            result = days_between(result, x2, op)
                            print("Result : " + str(result))

                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                            values('pk', 'c_v')
                        print("Rs :")
                        print(rs)
                        rs_pk.append(rs[0]['pk'])
                        rs_val.append(rs[0]['c_v'])
                        print("Final Result : " + str(result))
                    else:
                        print('NORMAL CALCULATION')
                        print('**************************************************************************************')
                        x1 = tmp_list[0]
                        x2 = tmp_list[2]
                        op = tmp_list[1]

                        print(x1)
                        print(x2)
                        print(op)
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                        result = operation(x1, x2, op)
                        print("1st Time result : " + str(result))
                        for y in range(3, len(tmp_list) - 1, 2):
                            op = tmp_list[y]
                            x2 = tmp_list[y + 1]
                            result = operation(result, x2, op)
                            print("Result : " + str(result))
                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                            values('pk', 'c_v')
                        print("Rs :")
                        print(rs)
                        rs_pk.append(rs[0]['pk'])
                        rs_val.append(rs[0]['c_v'])
                        print("Final Result : " + str(result))

        except Exception as e:
            return HttpResponse(e)


def calc_save(request):
    if request.method == 'POST':
        try:
            user = Login.objects.get(id=request.session['user_id'])
            createdby = user.email

            # ARRAY WITH COLUMN NAME
            vals = request.POST.getlist('arr_val[]')
            # ARRAY WITH COLUMN IDS
            ids = request.POST.getlist('arr_ids[]')
            # RESULTANT COLUMN NAME
            rs_column = request.POST['rs_column']
            # TABLE ID
            fk = request.POST['fk']
            max_row = request.POST['mx']

            print("vals : ")
            print(vals)

            print("ids : ")
            print(ids)

            print("RESULTANT COLUMN NAME : " + str(rs_column))
            print("TABLE ID : " + str(fk))
            print("MAX ROW : " + str(max_row))

            # CHECKING  ANY DATE DATE COULS IN LIST
            t = ['Date']
            dumb_ids = []
            for k in range(0, len(ids), 2):
                print("removing const")
                if ids[k] != 'const':
                    dumb_ids.append(ids[k])
            print("dumb ids : ")
            print(dumb_ids)
            num_type = ['Number', 'Numeric']
            calc_type = "Nothing"
            if Basecolumns.objects.filter(Q(pk__in=dumb_ids) & (Q(d_type__in=t) | Q(calc_type__in=t))).count() >= 1:
                print("calculatin have date and const")
                if len(ids) == 3:
                    print("length 3")
                    x1 = ids[0]
                    op = ids[1]
                    x2 = ids[2]
                    d_x1 = []
                    d_x2 = []
                    d_row = []
                    check_type = False
                    x1_or_x2 = 0
                    const_position = 0
                    if x1 == 'const':
                        check_type = True
                        x1_or_x2 = 1
                        const_position = 1
                        for m in range(0, int(max_row)):
                            d_x1.append(vals[0])
                    elif Basecolumns.objects.filter(Q(pk=x1) & (Q(d_type__in=num_type) | Q(calc_type__in=num_type))).count() == 1:
                        print("constant as column with position 1 in x1")
                        check_type = True
                        x1_or_x2 = 1
                        const_position = 1
                        data_x1 = Basedetails.objects.filter(bc_fk=x1).values('pk', 'c_v', 'bc_fk', 'row_num')
                        for item in data_x1:
                            d_x1.append(item['c_v'])
                    else:
                        # fetch vales related to column x1  form base details
                        data_x1 = Basedetails.objects.filter(bc_fk=x1).values('pk', 'c_v', 'bc_fk', 'row_num')
                        for item in data_x1:
                            d_x1.append(item['c_v'])
                            d_row.append(item['row_num'])

                    if x2 == 'const':
                        check_type = True
                        x1_or_x2 = 2
                        const_position = 2
                        for m in range(0, int(max_row)):
                            d_x2.append(vals[2])
                    elif Basecolumns.objects.filter(Q(pk=x2) & (Q(d_type__in=num_type) | Q(calc_type__in=num_type))).count() == 1:
                        print("constant as column with position 1 in x2")
                        check_type = True
                        x1_or_x2 = 2
                        const_position = 2
                        data_x2 = Basedetails.objects.filter(bc_fk=x2).values('pk', 'c_v', 'bc_fk', 'row_num')
                        for item in data_x2:
                            d_x2.append(item['c_v'])
                    else:
                        data_x2 = Basedetails.objects.filter(bc_fk=x2).values('pk', 'c_v', 'bc_fk', 'row_num')
                        for item in data_x2:
                            d_x2.append(item['c_v'])
                            d_row.append(item['row_num'])

                    # result valuse
                    result_arr_val = []
                    # result row
                    result_arr_row = []
                    # perform 1st time operation
                    type_of_op = ''
                    if check_type:
                        calc_type = 'Date'
                        print("date calculate with constant")
                        type_of_op = 'Date_With_Const'
                        print(d_x1)
                        print(d_x2)
                        for item in range(0, len(list(d_x1))):
                            if x1_or_x2 == 1:
                                res_val = days_betwenn_constant(d_x2[item], d_x1[item], op)
                                result_arr_val.append(res_val)
                            elif x1_or_x2 == 2:
                                print('second paramter is contanst')
                                res_val = days_betwenn_constant(d_x1[item], d_x2[item], op)
                                result_arr_val.append(res_val)

                            result_arr_row.append(d_row[item])
                        print(result_arr_val)
                    else:
                        # RESULT VIL BE NUMERIC
                        calc_type = 'Numeric'
                        print("date calculate")
                        type_of_op = 'Date_Calc'
                        for item in range(0, len(list(d_x1))):
                            res_val = days_between(d_x1[item], d_x2[item], op)
                            result_arr_val.append(res_val)
                            result_arr_row.append(d_row[item])
                        print(result_arr_val)
                    cal_column_creation(fk, createdby, rs_column, max_row, result_arr_val, result_arr_row, calc_type)
                    adding_equation_to_calc_table(fk, vals, ids, rs_column, createdby, type_of_op, const_position)
                    return JsonResponse({'Result': 'done'})
            elif Basecolumns.objects.filter(Q(pk__in=dumb_ids) & ~Q(d_type__in=t)).count() == len(dumb_ids) or\
                    Basecolumns.objects.filter(Q(pk__in=dumb_ids) & ~Q(d_type__in=t)).count() == len(dumb_ids)-1:
                calc_type = 'Nothing'
                print("Normal calculation without date")
                """
                length = 5  equatiion = a+b-c
                position = 0  1  2  3  4 --> a  +  b  -  c
                item --> 0      x1 = 0-->a     op = 0+1-->+    x2 = 0+2 -->b
                """
                x1 = ids[0]
                op = ids[1]
                x2 = ids[2]
                d_x1 = []
                d_x2 = []
                row_x1 = []
                if x1 == 'const':
                    for m in range(0, int(max_row)):
                        d_x1.append(vals[0])
                else:
                    # fetch vales related to column x1  form base details
                    data_x1 = Basedetails.objects.filter(bc_fk=x1).values('pk', 'c_v', 'bc_fk', 'row_num')
                    for item in data_x1:
                        d_x1.append(item['c_v'])
                        row_x1.append(item['row_num'])

                if x2 == 'const':
                    for m in range(0, int(max_row)):
                        d_x2.append(vals[2])
                else:
                    # fetch vales related to column x2  form base details
                    data_x2 = Basedetails.objects.filter(bc_fk=x2).values('pk', 'c_v', 'bc_fk', 'row_num')
                    for item in data_x2:
                        d_x2.append(item['c_v'])
                        if x2 != 'const':
                            row_x1.append(item['row_num'])
                # result valuse
                result_arr_val = []
                # result row
                result_arr_row = []
                # perform 1st time operation
                for item in range(0, len(list(d_x1))):
                    res_val = operation(d_x1[item], d_x2[item], op)
                    result_arr_val.append(res_val)
                    result_arr_row.append(row_x1[item])
                step = 2
                d_x1.clear()
                d_x2.clear()
                for item in range(3, len(ids), step):
                    """
                    item ---> 3     x1 = 0-->-      op = 0+1-->c
                    """
                    op = ids[item]
                    x2 = ids[item+1]
                    if x2 == 'const':
                        for m in range(0, int(max_row)):
                            d_x2.append(vals[item+1])
                    else:
                        print("op form loop : "+op)
                        print("x2 from loop : "+x2)
                        data_x2 = Basedetails.objects.filter(bc_fk=x2).values('pk', 'c_v', 'bc_fk')
                        for z in data_x2:
                            d_x2.append(z['c_v'])

                    for item in range(0, len(list(d_x2))):
                        res_val = operation(result_arr_val[item], d_x2[item], op)
                        result_arr_val[item] = res_val
                cal_column_creation(fk, createdby, rs_column, max_row, result_arr_val, result_arr_row, calc_type)
                adding_equation_to_calc_table(fk, vals, ids, rs_column, createdby, 'Normal_calc', 0)
                return JsonResponse({'vals': vals, 'ids': ids})
        except Exception as e:
            return HttpResponse(e)



def datatype_convertion(num):
    try:
        float(num)
        print("###########################")
        return float(num)
    except ValueError:
        return int(num)


def operation(num1=0, num2=0, opr=""):
    print("=== SARTING CLAC ===")
    print("opr : " + str(opr))
    print("num1 : " + str(num1))
    print("num2 : " + str(num2))
    result = 0

    num1 = datatype_convertion(num1)
    num2 = datatype_convertion(num2)

    if opr == '+':
        result = num1 + num2
    elif opr == '-':
        result = num1 - num2
    elif opr == '*':
        result = num1 * num2
    elif opr == '/':
        result = num1 / num2
        if isinstance(result, float):
            result = round(result, 2)
    elif opr == '%':
        result = num1 % num2
    elif opr == '>':
        if num1 > num2:
            result = num1
        else:
            result = num2
    elif opr == '<':
        if num1 < num2:
            result = num1
        else:
            result = num2
    print("%$(&&&&&((*&&")
    print(result)
    return result


def days_between(d1, d2, op):
    d1 = d1.split('-')
    d2 = d2.split('-')
    d1 = date(int(d1[0]), int(d1[1]), int(d1[2]))
    d2 = date(int(d2[0]), int(d2[1]), int(d2[2]))
    print(d1)
    print(d2)
    if op == '+':
        return abs((d1 + d2).days)
    elif op == '-':
        print('date minus : ')
        print(abs(d1 - d2).days)
        return abs(d1 - d2).days


def days_betwenn_constant(d1, d2, op):
    d1 = d1.split('-')
    d1 = str(d1[0]) + str(d1[1]) + str(d1[2])
    d1 = datetime.strptime(d1, "%Y%m%d").date()
    print("*******")
    print("D2 : " + str(d2))
    print("D1 : " + str(d1))
    print("*******")
    d2 = int(d2)
    if op == '+':
        print('tttttttttttttttttt')
        rs = d1 + timedelta(days=d2)
        rs = str(rs).split()
        print(rs)
        return rs[0]


def cal_column_creation(fk, createdby, colname, max_row, result_arr_val, result_arr_row, calc_type):
    try:
        print("FK : "+str(fk))
        print("COL NAME: "+colname)
        print("MAX ROW : "+max_row)
        print("CREATED BY : "+createdby)

        alls = Base.objects.filter(Q(pk=fk) & Q(created_by=createdby)).values('pk')
        print("PK : "+str(alls[0]['pk']))
        Basecolumns.objects.create(c_name=colname, base_fk=alls[0]['pk'], d_type="Calc", d_size=20, calc_type=calc_type)
        querysets = Basecolumns.objects.filter(base_fk=fk).values('pk')
        a = []
        for item in querysets:
            a.append(item['pk'])
        print("A [] : ")
        print(a)
        max_row = int(max_row) + 1
        f = Basecolumns.objects.latest('id')
        for item in range(1, int(max_row)):
            for x in range(0, len(result_arr_row)):
                if int(result_arr_row[x]) == item:
                    Basedetails.objects.create(c_v=result_arr_val[x], bc_fk=f, row_num=item)
    except Exception as e:
        return HttpResponse(e)


# ADDING CALCULATION COLUMN EQUATION TO TABLE
def adding_equation_to_calc_table(fk, vals, ids, rs_column, createdby, type_of_calc, position):
    formated_ids = ''
    formated_vals = ''
    for item in range(0, len(ids)):
        formated_ids = formated_ids + ids[item] + ','
        formated_vals = formated_vals + vals[item] + ','
    print("formated_ids : " + formated_ids)
    print("formated_vals : " + formated_vals)
    col_id = Basecolumns.objects.filter(Q(c_name=rs_column) & Q(base_fk=fk)).values('pk')
    col_id = col_id[0]['pk']
    print("col_id : " + str(col_id))
    Calculation.objects.create(fk_table=fk, fk_column=col_id, equ=formated_ids, equ_normal=formated_vals,
                               createdby=createdby, type_of_calc=type_of_calc, const_position=position)
    print("Equation added to table")


def Editinmodal(request):
    if request.method == "POST":
        try:
            detail_id = request.POST['key']
            value = request.POST['value']
            table_id = request.POST['table_id']

            base_data = Basedetails.objects.get(id=detail_id)

            det_id=Basecolumns.objects.filter(Q(base_fk=table_id) | Q(d_type=table_id)).values('pk')
            print(det_id)
            detailids=[]
            for items in det_id:
               detailids.append(items['pk'])
            print(detailids)

            base_data_c_val=base_data.c_v
            print(base_data_c_val)

            basedats_cv= Basedetails.objects.filter(Q(bc_fk__in=detailids) & Q(c_v=base_data_c_val)).values('c_v','pk')
            print(basedats_cv)

            row_no = base_data.row_num
            rs_pk = []
            rs_val = []
            cv_data=[]
            for item in basedats_cv:
                cv_data.append(item['pk'])

            d_count=Basedetails.objects.filter(pk__in=cv_data).count()
            if d_count >= 1:
                Basedetails.objects.filter(pk__in=cv_data).update(c_v=value)

            data = Calculation.objects.filter(fk_table=table_id).values('equ', 'fk_column', 'equ_normal',
                                                                            'type_of_calc', 'const_position')

            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            print(data)
            data_tmp = list(data)
            for item in data_tmp:
                tmp_list = str(item['equ']).split(',')
                equ_normal = str(item['equ_normal']).split(',')
                print("Equation : ")
                print(tmp_list)
                for item_x in range(0, len(tmp_list) - 1, 2):
                    if tmp_list[item_x] == 'const':
                        tmp_list[item_x] = equ_normal[item_x]
                    else:
                        c_id = int(tmp_list[item_x])
                        print("C_id : " + str(c_id))
                        val = Basedetails.objects.filter(Q(bc_fk=c_id) & Q(row_num=row_no)).values('pk', 'c_v')
                        if len(list(val)) != 0:
                            print("Val : ")
                            print(val)
                            tmp_list[item_x] = val[0]['c_v']
                        else:
                            tmp_list[item_x] = 0
                print("###### Formted equation : ######")
                print(tmp_list)
                if item['type_of_calc'] == 'Date_With_Const':
                    if data[0]['const_position'] == 1:
                        print("DATE CALCILATION WITH CONST POSITION 1")
                        x1 = tmp_list[0]
                        x2 = tmp_list[2]
                        op = tmp_list[1]
                        result = days_betwenn_constant(x1, x2, op)
                        print("1st Time result : " + str(result))
                        for y in range(3, len(tmp_list) - 1, 2):
                            op = tmp_list[y]
                            x2 = tmp_list[y + 1]
                            result = days_betwenn_constant(result, x2, op)
                            print("Result : " + str(result))
                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(
                            c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                            values('pk', 'c_v')
                        print("Rs :")
                        print(rs)
                        rs_pk.append(rs[0]['pk'])
                        rs_val.append(rs[0]['c_v'])
                        print("Final Result : " + str(result))
                    else:
                        print("DATE CALCULATION WITH CONST POSITION 2")
                        x1 = tmp_list[0]
                        x2 = tmp_list[2]
                        op = tmp_list[1]
                        result = days_betwenn_constant(x1, x2, op)
                        print("1st Time result : " + str(result))
                        for y in range(3, len(tmp_list) - 1, 2):
                            op = tmp_list[y]
                            x2 = tmp_list[y + 1]
                            result = days_betwenn_constant(result, x2, op)
                            print("Result : " + str(result))
                        Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(
                            c_v=result)
                        rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                            values('pk', 'c_v')
                        print("Rs :")
                        print(rs)
                        rs_pk.append(rs[0]['pk'])
                        rs_val.append(rs[0]['c_v'])
                        print("Final Result : " + str(result))
                elif item['type_of_calc'] == 'Date_Calc':
                    print("DATE CALCULATION NORMAL")
                    x1 = tmp_list[0]
                    x2 = tmp_list[2]
                    op = tmp_list[1]
                    print("x1 : " + str(x1) + "op : " + str(op) + "x2 : " + str(x2))
                    result = days_between(x1, x2, op)
                    print("1st Time result : " + str(result))
                    for y in range(3, len(tmp_list) - 1, 2):
                        op = tmp_list[y]
                        x2 = tmp_list[y + 1]
                        result = days_between(result, x2, op)
                        print("Result : " + str(result))

                    Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                    rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                        values('pk', 'c_v')
                    print("Rs :")
                    print(rs)
                    rs_pk.append(rs[0]['pk'])
                    rs_val.append(rs[0]['c_v'])
                    print("Final Result : " + str(result))
                else:
                    print('NORMAL CALCULATION')
                    x1 = tmp_list[0]
                    x2 = tmp_list[2]
                    op = tmp_list[1]

                    result = operation(x1, x2, op)
                    print("1st Time result : " + str(result))
                    for y in range(3, len(tmp_list) - 1, 2):
                        op = tmp_list[y]
                        x2 = tmp_list[y + 1]
                        result = operation(result, x2, op)
                        print("Result : " + str(result))
                    Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)).update(c_v=result)
                    rs = Basedetails.objects.filter(Q(bc_fk=item['fk_column']) & Q(row_num=row_no)). \
                        values('pk', 'c_v')
                    print("Rs :")
                    print(rs)
                    rs_pk.append(rs[0]['pk'])
                    rs_val.append(rs[0]['c_v'])
                    print("Final Result : " + str(result))



            return JsonResponse({'data': True})
        except Exception as e:
            print(e)
            return HttpResponse(e)


def forgetpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        user = Login.objects.get(email=email)
        current_site = get_current_site(request)
        email_subject = 'Reset the Password'
        message = render_to_string('resetpass.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': password_reset_token.make_token(user),
        })
        to_email = email
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        messages.success(request, 'We have sent you an reset link in the mail,'
                                  ' please confirm your email address to reset')
    return render(request, "forgetpass.html")


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = Login.objects.get(pk=uid)
        print(user.id)
        return render(request, 'passwordset.html', {'user': user})
    except Exception as e:
        print(e)
        return HttpResponse(e)


def Newpassword(request):
    try:
        if request.method == "POST":
            user = Login.objects.get(id=request.POST['id'] )
            password = request.POST['password']
            print(user.password)
            update = 0
            if user.password != password:
                user.password = password
                update += 1
            if update > 0:
                user.save()
                messages.success(request, 'Password has been reset.')
                return HttpResponseRedirect('/login')
            return JsonResponse({'data': 'updated'})
    except Exception as e:
        print(e)
        return HttpResponse(e)


def Invite(request):
    if request.method == "POST":
        email = request.POST['email']
        user = Login.objects.get(email=email)
        user.save()
        current_site = get_current_site(request)
        email_subject = 'Invitation'
        message = render_to_string('invitemail.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': Invite_token.make_token(user),
        })
        to_email = user.email
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        messages.success(request, 'We have sent you  link in the mail, please confirm your email address to Login')
    return HttpResponseRedirect('/index')


# table FILTER
def Col_filter(request):
    if request.method == "POST":
        try:
            base_id = request.POST['base_id']
            l = request.POST['v_length']
            col_v = []
            base_col = []
            base_details = []
            r_n = []
            for i in range(0, int(l)):
                col_v.append(request.POST.getlist('col_values[]')[i])

            print(col_v)
            base = Basecolumns.objects.filter(base_fk=base_id).values('pk', 'c_name', 'base_fk')
            for items in base:
                base_col.append(items['pk'])
            print(base_col)
            r_c = Basedetails.objects.filter(Q(bc_fk__in=base_col) & Q(c_v__in=col_v)).values('pk', 'c_v', 'row_num').\
                count()
            b_details = Basedetails.objects.filter(Q(bc_fk__in=base_col) & Q(c_v__in=col_v)).\
                values('pk', 'c_v', 'row_num')
            print(list(b_details))
            for items in b_details:
                r_n.append(items['row_num'])
            print(r_n)

            print(r_c)

            base_data = Basedetails.objects.filter(Q(row_num__in=r_n) & Q(bc_fk__in=base_col)).\
                values('c_v', 'pk', 'row_num').order_by('row_num', 'bc_fk')
            print(base_data)

            # Final result of row values
            column_values = []
            # Final result of row value Id
            colum_values_id = []
            # Final reslut of row number
            column_row_val = []

            # converting fetched basedetails object to list
            querysets = list(base_data)
            for item in base_data:
                column_values.append(item['c_v'])
                colum_values_id.append(item['pk'])
                column_row_val.append(item['row_num'])

            # Length of
            length_base_details = len(column_values)
            length_base_column = Basecolumns.objects.filter(base_fk=base_id).count()
            total = int(length_base_details/length_base_column)

            # Last row number ---> appending to table body as id
            if len(column_row_val) == 0:
                max_row = 0
            else:
                max_row = max(column_row_val)

            mylist = zip(column_values, colum_values_id, column_row_val)
            mylist_length = len(column_values)

            # return JsonResponse({'base_data':list(base_data),'col_names':list(base)})
            return JsonResponse({'base_data': list(base_data), 'col_names': list(base), 'bc': length_base_column,
                                 'mylist_length': mylist_length, 'mylist': list(mylist), 'max_row': max_row})

        except Exception as e:
            print(e)
            return HttpResponse(e)


def importx(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            table_id = request.POST['id']
            uploaded_file = request.FILES['files']
            max_row = int(request.POST['max_row'])

            table_real_name = Base.objects.get(id=table_id)
            table_owner = table_real_name.created_by
            table_real_name = table_real_name.base_name

            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name,uploaded_file)
            name = 'media/' + name
            path = os.path.join(BASE_DIR, name)
            workbook = xlrd.open_workbook(path)
            sheet = workbook.sheet_by_index(0)
            sheet.cell_value(0,0)
            col_name = []
            for col in range(sheet.ncols):
                col_name.append(str(sheet.cell_value(0, col)).strip().lower())

            data = [[sheet.cell_value(r, c) for c in range (sheet.ncols)] for r in range(sheet.nrows)]
            base = Basecolumns.objects.filter(base_fk=table_id).values('pk', 'c_name', 'base_fk')
            base_col = []
            base_col_ids = []
            for i in base:
                base_col.append(i['c_name'])
                base_col_ids.append(i['pk'])

            check_val = 0

            print("col names : ")
            print(col_name)
            print("check val default : " + str(check_val))
            print('base col : ')
            print(base_col)

            if len(col_name) == len(base_col):
                for item in range(0, len(col_name)):
                    b_c = Basecolumns.objects.filter(Q(base_fk=table_id) & Q(c_name=col_name[item])).\
                        values('pk', 'c_name', 'base_fk')
                    if Basecolumns.objects.filter(Q(base_fk=table_id) & Q(c_name=col_name[item])).count() == 1:
                        col_name[item] = b_c[0]['pk']
                    else:
                        check_val = 1

            print("check val updated : " + str(check_val))
            print('updated col_name')
            print(col_name)
            print(data)
            data_count = Base.objects.filter(Q(created_by=login_user) & Q(pk=table_id)).count()
            if data_count == 1:
                print("IMPORT X")
                print("================================================================================")
                if check_val == 0:
                    print("IMPORT  CHCK VAL")
                    print("****************************************************************************")
                    print(data)
                    for item in range(1, len(data)):
                        max_row += 1
                        print(max_row)
                        for x in range(0, len(col_name)):
                            print("&&&&&&&&&&&&&&&&&&&&&&&")
                            try:
                                Basedetails.objects.create(c_v=data[item][x], bc_fk=col_name[x], row_num=max_row)
                                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            except Exception as e:
                                return HttpResponse(e)

                return JsonResponse({'Result': 'Root User Added Records'})
            elif data_count != 1:
                # FETCHING USER DETAILS FROM USER LIST TABLE
                permissions_list = user_List.objects.filter(Q(user_id=login_user) & Q(table_id=table_id)).values('role')
                permitted_rolse = []
                for item in permissions_list:
                    permitted_rolse.append(item['role'])
                rolse_data = permissions.objects.filter(pk__in=permitted_rolse).values('add_data')
                if len(list(rolse_data)) == 1:
                    if rolse_data[0]['add_data'] == 'true':
                        if check_val == 0:
                            for item in range(1, len(data)):
                                max_row += 1
                                for x in range(0, len(col_name)):
                                    Basedetails.objects.create(c_v=data[item][x], bc_fk=col_name[x], row_num=max_row)
                        print("Notification Sending......")
                        notfy = user_List.objects.filter(Q(role__in=permitted_rolse) & Q(table_id=table_id)) \
                            .values('user_id')
                        msg = str(login_user) + ' Added Records Into ' + str(table_real_name)
                        for x in notfy:
                            if x['user_id'] != login_user:
                                notification_sender(sender_id=request.session['user_id'],
                                                    user_email=x['user_id'], status=1,
                                                    heading="Records Added", message=msg)
                        # SENDING TO TABLE OWNER
                        notification_sender(sender_id=request.session['user_id'], user_email=table_owner,
                                            status=1, heading="Records Added", message=msg)
                        return JsonResponse({'Result': 'Non Root User Added Records'})
            else:
                messages.success(request, 'User have no permission Add Records')
                return JsonResponse({'Result': 'User have no permission for Add Records'})
        except Exception as e:
            return HttpResponse(e)


# EMAIL VALIDATION FUNCTION
def email_validation(email):
    """
    param:email
    return true or false
    """
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False


def permission_user_list(request):

    # CHECKING SESSION ID IN LOGIN TABLE FOR IDENTIFYING USER
    user = Login.objects.get(id=request.session['user_id'])
    user_email = user.email
    login_obj = Login.objects.all().exclude(id=request.session['user_id'])
    account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
    profiles =designation.objects.filter(created_by=request.session['user_id']).values('profile')
    designations=designation.objects.all()
    # FETCHING THE MODELS RELATED TO USER
    sub_tbl = Group_model_secondary.objects.all()
    tmp_menu_pk = []
    for item in sub_tbl:
        tmp_menu_pk.append(item.secondary_tables_id)
    menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))
    # FETCHING THE REPORTS RELATED TO USER
    reports = Report.objects.filter(created_by=user_email)
    # FETING DATA FROM USER LIST TABLE WHERE ADMIN ID = WHO SIGNED IN
    user_list = user_List.objects.filter(admin_id=request.session['user_id'])\
        .values('pk', 'user_id', 'created_date', 'role', 'profile').order_by('-created_date').distinct()

    # SELECTING EMAIL ID'S OF USERS
    emails = []
    for item in user_list:
        emails.append(item['user_id'])

    details = Login.objects.filter(email__in=emails).values('pk', 'name', 'email')
    ids = []
    for item in details:
        ids.append(item['pk'])
    image = Profile.objects.filter(log_fk__in=ids).values('user_image', 'log_fk')
    # CURRENT DATE
    c_date = datetime.now().strftime("%Y-%m-%d")

    main_list = []
    main_email = []
    for item in user_list:
        name ='Unknown'
        image_path = 'media/user.jpg'
        for x in details:
            if item['user_id'] == x['email']:
                name = x['name']
            for y in image:
                if item['user_id'] == x['email'] and y['log_fk'] == x['pk']:
                    image_path = y['user_image']

        profile = item['profile']
        # FETCHING ROLE IN WORDS VIA ID
        role = permissions.objects.get(id=item['role'])
        created_user=role.created_user
        role = role.role
        email_id = item['user_id']
        created_date = item['created_date']
        row_dict = {'name': name, 'image': image_path, 'profile': profile, 'role': role, 'created_date': created_date,
                    'email_id': email_id,'created_user':created_user}
        if len(main_email) == 0:
            print("***********************")
            print(email_id)
            main_email.append(email_id)
            main_list.append(row_dict)
        else:
            if email_id in main_email:
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                    print(email_id)
            else:
                main_email.append(email_id)
                main_list.append(row_dict)
                print(email_id)

    # FETCHING ROLES / GROUP NAME CREATED BY CURRENT USER
    rolse_fr_per = permissions.objects.filter(created_user=request.session['user_id']).values('pk', 'role')
    pro = Profile.objects.filter(log_fk=request.session['user_id'])
    # Profile pic avilable or not
    profile_pic = ''
    if len(list(pro)) != 0:
        if pro[0].user_image == None:
            profile_pic = 'media/user.jpg'
        else:
            profile_pic = pro[0].user_image.url
    else:
        profile_pic = 'media/user.jpg'

    nti_msg = notification_Messages.objects.filter(Q(reciever_id=user_email) & Q(status=1)) \
        .values('pk', 'heading', 'message', 'sender_id')
    final_nti_msg = []
    for item in nti_msg:
        if Profile.objects.filter(log_fk=item['sender_id']).count() == 1:
            pic_data = Profile.objects.get(log_fk=item['sender_id'])
            if pic_data.user_image == None:
                dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                       'pic': 'media/user.jpg'}
                final_nti_msg.append(dic)
            else:
                dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                       'pic': pic_data.user_image.url}
                final_nti_msg.append(dic)
        else:
            dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'], 'pic': 'media/user.jpg'}
            final_nti_msg.append(dic)
    nti_count = len(list(nti_msg))

    up = main_list

    print("#############")
    print(up)
    print("################")

    if request.session.has_key('user_id'):
        return render(request, 'Users.html', {'menus': menus, 'data': main_list, 'df_image': 'default_image',
                                              'c_date': datetime.today().date(), 'rolse_fr_per': rolse_fr_per, 'pro': pro,
                                              'user': user, 'profile_pic': profile_pic, 'nti_count': nti_count,'login_obj':login_obj,
                                              'nti_msg': final_nti_msg,'reports':reports,'account_details':account_details,
                                              'profiles':profiles,'designations':designations})


def email_autoconplite(request):
    loged_user = Login.objects.get(id=request.session['user_id'])
    loged_user_email = loged_user.email
    loged_user_company=loged_user.company_name
    print("Logind User : " + str(loged_user))
    email = Login.objects.filter(company_name=loged_user_company).values('email').exclude(email=loged_user_email )
    user_email = []
    for item in email:
        if item['email'] != loged_user:
            user_email.append(item['email'])
    print(user_email)
    return JsonResponse({'email': user_email})


def user_list_update(request):
    if request.method == "POST":
        try:
            user_email = request.POST['email']
            role = request.POST['role']
            profile = request.POST['profile']
            table_id_all = request.POST.getlist('table_id[]')
            report_id_all = request.POST.getlist('reports_id[]')
            print(report_id_all)


            # table_id = request.POST['table_id']
            print(table_id_all)
            print(len(table_id_all))
            print(len(report_id_all))

            user = Login.objects.get(id=request.session['user_id'])
            email = user.email
            message = email + ' Assigned New Role For you please Check Details'

            if Login.objects.filter(email=user_email).count() == 1:
                for x in table_id_all:
                    table_id=int(x)
                    data1 = user_List.objects.\
                        filter(Q(user_id=user_email) & Q(admin_id=request.session['user_id']) & Q(table_id=table_id) ).\
                        count()

                    if data1 == 0:
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        user_List.objects.create(user_id=user_email, admin_id=request.session['user_id'],
                                                profile=profile, role=role, table_id=table_id,)
                        notification_Messages.objects.create(sender_id=request.session['user_id'],
                                                            reciever_id=user_email, send_date=datetime.today().date(),
                                                            status=1, heading='New Permission', message=message)
                    else:
                        return JsonResponse({'Message': 'Already Exist', 'Type': 'danger'})
                for x in report_id_all:
                    report=int(x)
                    data2 = user_List.objects.\
                        filter(Q(user_id=user_email) & Q(admin_id=request.session['user_id']) & Q(report_id=report) ).\
                        count()
                    if data2 == 0:
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        user_List.objects.create(user_id=user_email, admin_id=request.session['user_id'],
                                                    profile=profile, role=role, report_id=report)
                        notification_Messages.objects.create(sender_id=request.session['user_id'],
                                                            reciever_id=user_email, send_date=datetime.today().date(),
                                                            status=1, heading='New Permission', message=message)
                    else:
                        return JsonResponse({'Message': 'Already Exist', 'Type': 'danger'})

                return JsonResponse({'Message': 'User Added Successfully', 'Type': 'success'})


        except Exception as e:
            return HttpResponse(e)

# DELETING USERS FORM USER_LIST TABLE
def delete_user_from_list(request):
    pass


def save_role(request):
    if request.method == "POST":
        try:
            role_name = request.POST['role_name']
            about = request.POST['about']
            add_user = request.POST['add_user']
            create_table = request.POST['create_table']
            add_data = request.POST['add_data']

            delete_data = request.POST['delete_data']
            update_data = request.POST['update_data']
            add_fields = request.POST['add_fields']
            delete_fields = request.POST['delete_fields']
            update_fields = request.POST['update_fields']
            create_report = request.POST['create_report']
            view_report = request.POST['view_report']
            delete_report = request.POST['delete_report']
            print(update_fields)
            r_count=permissions.objects.filter(Q(created_user=request.session['user_id']) & Q(role=role_name)).count()
            if r_count == 0:

                permissions.objects.create(created_user=request.session['user_id'], role=role_name, about=about,
                                       add_user=add_user, create_tables=create_table, add_data=add_data,
                                       delete_data=delete_data, update_data=update_data, add_col=add_fields,
                                       delete_col=delete_fields, update_col=update_fields,
                                       delete_report=delete_report,create_report=create_report,view_report=view_report)
            else:
                return JsonResponse({'Message': 'Already Exist', 'Type': 'danger'})
            return JsonResponse({'data': 'ok'})

        except Exception as e:
            return HttpResponse(e)
    else:
        pass


def role_update_fetch(request):
    if request.method == "POST":
        try:
            role_id = request.POST['role_id']
            data = permissions.objects.filter(pk=role_id).values('role', 'about', 'add_user', 'create_tables',
                                                                 'add_data', 'delete_data', 'update_data',
                                                                 'add_col', 'delete_col', 'update_col',
                                                                 'create_report','view_report','delete_report')
            return JsonResponse({'Result':list(data)})
        except Exception as e:
            return HttpResponse(e)


def update_role(request):
    if request.method == "POST":
        try:
            role_id = request.POST['role_id']
            role_name = request.POST['role_name']
            about = request.POST['about']
            add_user = request.POST['add_user']
            create_table = request.POST['create_table']
            add_data = request.POST['add_data']

            delete_data = request.POST['delete_data']
            update_data = request.POST['update_data']
            add_fields = request.POST['add_fields']
            delete_fields = request.POST['delete_fields']
            update_fields = request.POST['update_fields']
            create_report = request.POST['create_report']
            view_report = request.POST['view_report']
            delete_report = request.POST['delete_report']


            permissions.objects.filter(pk=role_id).update(role=role_name, about=about,
                                       add_user=add_user, create_tables=create_table, add_data=add_data,
                                       delete_data=delete_data, update_data=update_data, add_col=add_fields,
                                       delete_col=delete_fields, update_col=update_fields,
                                       delete_report=delete_report,create_report=create_report,view_report=view_report)
            return JsonResponse({'data':'Updated'})
        except Exception as e:
            return HttpResponse(e)


def clear_notification(request):
    if request.method == "POST":
        try:
            n_id = request.POST['n_id']
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email

            data = notification_Messages.objects.get(id=n_id)
            if data.reciever_id == user_email:
                if notification_updates(n_id, 2):
                    return JsonResponse({'Result': 'Cleared'})
        except Exception as e:
            return HttpResponse(e)


def delete_notification(request):
    if request.method == "POST":
        try:
            n_id = request.POST['n_id']
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email

            data = notification_Messages.objects.get(id=n_id)
            if data.reciever_id == user_email:
                if notification_updates(n_id, 3):
                    return JsonResponse({'Result': 'Deleted'})
        except Exception as e:
            return HttpResponse(e)


def delete_notification_all(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email
            print("+++++++++++++++++")
            data = notification_Messages.objects.filter(Q(reciever_id=user_email) & Q(status=1)).update(status=2)
            print(data)
            return JsonResponse({'Result': 'Deleted All'})
        except Exception as e:
            return HttpResponse(e)


def imageprofile(request):
    if request.method == "POST":
        try:
            image = request.FILES['propic']
            fs = FileSystemStorage()
            name = fs.save(image.name, image)
            name = 'media/' + name
            print(name)
            path = os.path.join(BASE_DIR, name)
            print(path)
            print(image)
            # pro_obj =Profile.objects.filter(log_fk=request.session['user_id']).values('name','lname','phone','skype')
            # pro_obj=list(pro_obj)
            # print(pro_obj)
            if  Profile.objects.filter(log_fk=request.session['user_id']).count()== 0:
                Profile.objects.create(user_image=image,log_fk=request.session['user_id'],name='',lname='',
                location='',skype='')
                return HttpResponseRedirect('/userprofile')
            else:
                img_profile = Profile.objects.filter(log_fk=request.session['user_id']).values('user_image').count()
                if img_profile == 0:
                    pro = Profile.objects.get(log_fk=request.session['user_id'])
                    pro.user_image = image
                    pro.save()
                else:
                    pro = Profile.objects.get(log_fk=request.session['user_id'])
                    count = 0
                    if pro.user_image != image:
                        pro.user_image = image
                        count += 1
                        if count > 0:
                            pro.save()
                return HttpResponseRedirect('/userprofile')
            # return render(request, 'userdetails.html', {'pro':pro_obj,'form':pro_obj})
        except Exception as e:
            print(e)


# SCHEMA
def schema_fetchcolumns(request):
    try:
        if request.method == "POST":
            base_id = request.POST['base_id']
            base_col = Basecolumns.objects.filter(base_fk=base_id).values('pk', 'c_name')
            print(list(base_col))
            return JsonResponse({'data': list(base_col)})
    except Exception as e:
        print(e)


def schemasave(request):
    try:
        if request.method == "POST":
            base_id = request.POST['base_id']
            table_name = request.POST['table']
            col_name = request.POST.getlist('column_txt[]')
            print('name')
            print(col_name[0])
            col_count = len(col_name)
            print(col_count)
            created_by = Login.objects.filter(id=request.session['user_id']).values('email')
            email=created_by[0]['email']
            check_count = Base.objects.filter(Q(base_name=table_name) & Q(created_by=email)).count()
            if check_count == 0:
                Base.objects.create(base_name=table_name, fk=request.session['user_id'], created_by=email)
                base = Base.objects.get(base_name=table_name)
                base_pk = base.id
                print(base_pk)
                if col_name[0] == 'Select all':
                    base_cols = Basecolumns.objects.filter(base_fk=base_id).values('c_name', 'd_type', 'd_size')
                    print(list(base_cols))
                    col_array_len = len(list(base_cols))
                    print('col_array_len')
                    print(col_array_len)
                    for j in range (0, int(col_array_len)):
                        Basecolumns.objects.create(c_name=base_cols[j]['c_name'], base_fk=base_pk,
                                                   d_type=base_cols[j]['d_type'], d_size=base_cols[j]['d_size'])
                else:
                    for i in range(0, int(col_count)):
                        base_cols = Basecolumns.objects.filter(c_name=col_name[i]).values('d_type', 'd_size')
                        print('base_cols')
                        print(base_cols)
                        Basecolumns.objects.create(c_name=col_name[i], base_fk=base_pk, d_type=base_cols[0]['d_type'],
                                                   d_size=base_cols[0]['d_size'])
                messages.success(request, 'Table created')
            else:
                messages.success(request, 'Table Already Exist')
        return JsonResponse({'data': 'success'})
    except Exception as e:
        print(e)


# DELETE USER ACCOUNT
def delete_account(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email
            tmp_base = []
            data_base = Base.objects.filter(created_by=user_email).values('pk')
            for item in data_base:
                tmp_base.append(item['pk'])

            data_columns= Basecolumns.objects.filter(base_fk__in=tmp_base).values('pk')
            tmp_col = []
            for item in data_columns:
                tmp_col.append(item['pk'])

            Basedetails.objects.filter(bc_fk__in=tmp_col).delete()
            Basecolumns.objects.filter(base_fk__in=tmp_base).delete()
            Base.objects.filter(created_by=user_email).delete()

            Login.objects.filter(email=user_email).delete()
            if request.session.has_key('user_id'):
                # del request.session['user_id']
                request.session.flush()
            return HttpResponseRedirect('/login')
        except Exception as e:
            return HttpResponse(e)


def notification_sender(sender_id, user_email, status, heading, message):
    if notification_Messages.objects.create(sender_id=sender_id, reciever_id=user_email,
                                            send_date=datetime.today().date(), status=status, heading=heading,
                                            message=message):
        return True
    else:
        return False


# UPDATING NOTIFICATION STATUS FOR DELETE AND CLEAR
def notification_updates(n_id, status):
    notification_Messages.objects.filter(pk=n_id).update(status=status)
    return True


# Database and table hanbling
def Truncate_tables(request):
    try:

        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email
        base_ids = Base.objects.filter(created_by=user_email).values('pk')
        base_columns = Basecolumns.objects.filter(base_fk__in=base_ids).values('pk')
        Basedetails.objects.filter(bc_fk__in=base_columns).delete()
        return JsonResponse({'data': 'success'})
        # return HttpResponseRedirect('/index')
    except Exception as e:
        print(e)


def Delete_users(request):
    try:

        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email
        base_ids = Base.objects.filter(created_by=user_email).values('pk')
        report_ids = Report.objects.filter(created_by=user_email).values('pk')
        # print(base_ids)
        bids=[]
        rids=[]
        for item in base_ids:
            bids.append(item['pk'])
        for item in report_ids:
            rids.append(item['pk'])

        user_List.objects.filter(table_id__in=bids).delete()
        user_List.objects.filter(report_id__in= rids).delete()
        user_List.objects.filter(Q(table_id= '0')&Q(report_id='0')).delete()

        return JsonResponse({'data': success})
        # return HttpResponseRedirect('/permission_user_list')

    except Exception as e:
        print(e)


def Delete_tables(request):
    try:

        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email
        base_ids = Base.objects.filter(created_by=user_email).values('pk')
        # print(base_ids)
        base_columns = Basecolumns.objects.filter(base_fk__in=base_ids).values('pk')
        # print(base_columns)
        Basedetails.objects.filter(bc_fk__in=base_columns).delete()
        Basecolumns.objects.filter(base_fk__in=base_ids).delete()
        Base.objects.filter(created_by=user_email).delete()


        return JsonResponse({'data':success})
        # return HttpResponseRedirect('/index')
    except Exception as e:
        print(e)


# deactivate account
def disable_account(request):
    if request.method == "POST":
        try:
            dis_period=request.POST['disable_for']
            print(dis_period)
            if dis_period == '1 Day':
                period_end=datetime.today().date()+timedelta(days=1)
            elif dis_period == '1 Week':
                period_end=datetime.today().date()+timedelta(days=7)
            elif dis_period == '1 Month':
                period_end=datetime.today().date()+timedelta(days=30)
            elif dis_period == '1 Year':
                period_end=datetime.today().date()+timedelta(days=365)
            print(period_end)
            Login.objects.filter(pk=request.session['user_id']).update(is_disabled='true',disable_period=dis_period,disable_period_end=period_end)
            if request.session.has_key('user_id'):

                request.session.flush()
                messages.success(request, 'Account Deactivation Successfull')
            return HttpResponseRedirect('/login')

        except Exception as e:
            return HttpResponse(e)


##UPDATE USER
def pro_update_fetch(request):
    if request.method == "POST":
        try:
            pro_id = request.POST['pro_id']
            data = user_List.objects.filter(Q(user_id=pro_id)&Q(admin_id=request.POST['admin_id'])).\
                values('role', 'profile', 'table_id', 'admin_id','report_id')
            # print('profile_update')
            # print(data)
            return JsonResponse({'Result': list(data)})
        except Exception as e:
            return HttpResponse(e)



def update_pro(request):
    if request.method == "POST":
        try:
            # EMAIL ID
            pro_id = request.POST['pro_id']
            role = request.POST['role_name']
            profile = request.POST['profile']
            tbl_names_updated = request.POST.getlist('tbl_name[]')
            report_ids_updated = request.POST.getlist('report_id[]')
            adminid=request.POST['adminid']
            print(adminid)

            user_List.objects.filter(Q(user_id=pro_id) & Q(admin_id=adminid)).delete()
            count=user_List.objects.filter(Q(user_id=pro_id) & Q(admin_id=adminid)).count()
            print(count)
            if count == 0:
                for item in tbl_names_updated:

                    user_List.objects.create(user_id=pro_id, role=role, profile=profile, table_id=item,admin_id=adminid)

                for item in report_ids_updated:

                    user_List.objects.create(user_id=pro_id, role=role, profile=profile, report_id=item,admin_id=adminid)

            return JsonResponse({'data': 'Updated'})
        except Exception as e:
            return HttpResponse(e)

def report(request):
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email
            # reports=Report.objects.filter(created_by=user_email).values('pk', 'Reportname')

            sub_tbl = Group_model_secondary.objects.all()
            tmp_menu_pk = []
            for item in sub_tbl:
                tmp_menu_pk.append(item.secondary_tables_id)
            menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk)).values('base_name', 'pk')

            pro = Profile.objects.filter(log_fk=request.session['user_id'])
            login_obj = Login.objects.all().exclude(id=request.session['user_id'])
            account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
            designations=designation.objects.all()
            # PROFILE PIC AVAILABLE OR NOT
            profile_pic = ''
            if len(list(pro)) != 0:
                if pro[0].user_image == None:
                    profile_pic = 'media/user.jpg'
                else:
                    profile_pic = pro[0].user_image.url
            else:
                profile_pic = 'media/user.jpg'
            # PROFILE PIC END
            # REPORT and permitted report
            tmp_rids  = []
            rp = Report.objects.filter(created_by=user_email).values('pk')
            for item in rp:
                tmp_rids.append(item['pk'])
            print(tmp_rids)

            permissions_list = user_List.objects.filter(user_id=user_email).values('role')
            rep_role=[]
            for item in permissions_list:
                rep_role.append(item['role'])
            print(rep_role)

            rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).count()
            if rolse_data >= 1:
                per_rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).values('pk')
                tmp  = []
                for item in per_rolse_data:
                    tmp.append(item['pk'])
                print('tmp')
                print(tmp)
                r_id=user_List.objects.filter(Q(user_id=user_email)& Q(role__in=tmp)).values('report_id')

                for item in r_id:
                    tmp_rids.append(item['report_id'])
                print(tmp_rids)
            reports = Report.objects.filter(pk__in=tmp_rids).values('pk','Reportname')
            # PERMITTED  TABLES WITH REPORT CREATE PERMISSION
            tmp_cr=[]
            rolse_data_create= permissions.objects.filter(Q(pk__in=rep_role)& Q(create_report='true')).count()
            if rolse_data_create >= 1:
                per_rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(create_report='true')).values('pk')
                tmp2  = []
                for item in per_rolse_data:
                    tmp2.append(item['pk'])
                print('tmp2')
                print(tmp2)
                r_id_create=user_List.objects.filter(Q(user_id=user_email)& Q(role__in=tmp2)).values('table_id')
                print(r_id_create)
                for item in r_id_create:
                    tmp_cr.append(item['table_id'])
                print(tmp_cr)
                print('tmp_cr')
            permitted_tbl = Base.objects.filter(pk__in=tmp_cr).values('pk','base_name')
            print(permitted_tbl)



            return render(request, 'report.html', {'menus': menus, 'reports': reports,'profile_pic': profile_pic,
                                  'pro': pro,'user':user,'account_details':account_details,'permitted_tables':permitted_tbl,
                                  'login_obj':login_obj,'designations':designations})

        except Exception as e:
            print(e)
            return HttpResponse(e)


def reportfetch(request):
    try:
        if request.method == "POST":
            base_id = request.POST['base_id']

            base_col = Basecolumns.objects.filter(base_fk=base_id).values('pk', 'c_name')
            print(list(base_col))
            return JsonResponse({'data': list(base_col)})
    except Exception as e:
        print(e)


def reportsave(request):
    try:
        if request.method == "POST":
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email

            base_id = request.POST['base_id']
            rpt_name = request.POST['rpt_name']
            Drpt_name = request.POST['Drpt_name']
            col_name = request.POST.getlist('column_txt[]')
            print('name')
            print(col_name[0])
            col_count = len(col_name)
            print(col_count)
            Report.objects.create(Reportname=rpt_name,DetailRname= Drpt_name,table_id=base_id,
                    created_by=user_email)
            report_id =Report.objects.filter(Q(Reportname=rpt_name) & Q(created_by=user_email)).values('pk')
            print(report_id)
            if col_name[0] == 'Select all':
                base_cols= Basecolumns.objects.filter(base_fk=base_id).values('pk')
                print(list(base_cols))
                col_array_len = len(list(base_cols))
                print('col_array_len')
                print(col_array_len)
                for j in range (0,int(col_array_len)):
                    Reportcontent.objects.create(reportid=report_id[0]['pk'],column_id=base_cols[j]['pk'])

            else:
                for i in range (0,int(col_count)):
                    base_cols = Basecolumns.objects.filter(Q(c_name=col_name[i]) & Q(base_fk=base_id)).values('pk')
                    print('base_cols')
                    print(base_cols)
                    Reportcontent.objects.create(reportid=report_id[0]['pk'],column_id=base_cols[0]['pk'])
            messages.success(request, 'Successfully Added to Report')
        return JsonResponse({'data':'success'})
    except Exception as e:
        print(e)




def viewreport(request,pkp):
    try:
        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email
        menus = Base.objects.filter(created_by=user_email).values('base_name','pk')
        pro = Profile.objects.filter(log_fk=request.session['user_id'])
        account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
        login_obj = Login.objects.all().exclude(id=request.session['user_id'])
        designations=designation.objects.all()
        # Profile pic avilable or not
        profile_pic = ''
        if len(list(pro)) !=0:
            if pro[0].user_image == None:
                profile_pic = 'media/user.jpg'
            else:
                profile_pic = pro[0].user_image.url
        else:
            profile_pic = 'media/user.jpg'
        # reports=Report.objects.filter(created_by=user_email).values('pk','Reportname')
        # REPORT and permitted report
        tmp_rids  = []
        rp = Report.objects.filter(created_by=user_email).values('pk')
        for item in rp:
            tmp_rids.append(item['pk'])
        print(tmp_rids)

        permissions_list = user_List.objects.filter(user_id=user_email).values('role')
        rep_role=[]
        for item in permissions_list:
            rep_role.append(item['role'])
        print(rep_role)

        rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).count()
        if rolse_data >= 1:
            per_rolse_data = permissions.objects.filter(Q(pk__in=rep_role)& Q(view_report='true')).values('pk')
            tmp  = []
            for item in per_rolse_data:
                tmp.append(item['pk'])
            print('tmp')
            print(tmp)
            r_id=user_List.objects.filter(Q(user_id=user_email)& Q(role__in=tmp)).values('report_id')

            for item in r_id:
                tmp_rids.append(item['report_id'])
            print(tmp_rids)
        reports = Report.objects.filter(pk__in=tmp_rids).values('pk','Reportname')
        # REPORT and permitted report end
        report_data= Report.objects.filter(pk=pkp).values('DetailRname','pk','created_date')
        # CHECK DELETE REPORT PERMISSION
        del_rid=user_List.objects.filter(Q(report_id=pkp)& Q(user_id=user_email)).values('role')
        del_role=[]
        for item in del_rid:
            del_role.append(item['role'])
        del_per=permissions.objects.filter(Q(pk__in=del_role) & Q(delete_report='false')).count()
        del_per_check='True'
        if del_per != 0:
            del_per_check='false'

        # CHECK DELETE REPORT PERMISSION
        print('reportname')
        print(report_data)
        dname=report_data[0]['DetailRname']
        rdate=report_data[0]['created_date']

        report_content= Reportcontent.objects.filter(reportid=pkp).values('column_id')
        print('report_content')
        print(report_content)
        col_ids=[]
        for item in report_content:
            col_ids.append(item['column_id'])

        bc=len(col_ids)
        base_cols=Basecolumns.objects.filter(pk__in=col_ids).values('pk','c_name')
        print(base_cols)
        r_n=[]
        base_details=Basedetails.objects.filter(bc_fk__in=col_ids).values('pk','c_v','bc_fk','row_num')
        for items in base_details:
            r_n.append(items['row_num'])
        print(r_n)
        base_data = Basedetails.objects.filter(Q(row_num__in=r_n) & Q(bc_fk__in=col_ids)).\
            values('c_v', 'pk', 'row_num','bc_fk').order_by('row_num', 'bc_fk')
        print(base_data)
        # Final result of row values
        column_values = []
        # Final result of row value Id
        colum_values_id = []
        # Final reslut of row number
        column_row_val = []
        # Final reslut of data_type
        column_data_type=[]

        # converting fetched basedetails object to list
        querysets = list(base_data)
        for item in base_data:
            tmp_type = Basecolumns.objects.get(pk=item['bc_fk'])
            column_data_type.append(tmp_type.d_type)
            column_values.append(item['c_v'])
            colum_values_id.append(item['pk'])
            column_row_val.append(item['row_num'])

        # # Length of
        # length_base_details = len(column_values)
        # length_base_column = Basecolumns.objects.filter(base_fk=base_id).count()
        # total = int(length_base_details/length_base_column)

        # Last row number ---> appending to table body as id
        if len(column_row_val) == 0:
             max_row = 0
        else:
            max_row = max(column_row_val)

        mylist = zip(column_values, colum_values_id, column_row_val,column_data_type)
        mylist_length = len(column_values)
        mylist_length=len(list(base_details))


        return render(request,'reports.html',{'menus': menus,'report_data':report_data,'base_cols':base_cols,'base_details':base_details,
                                            'max_row':max_row,'mylist_length':mylist_length,'bc':bc,'mylist':mylist,'reports':reports,
                                            'id':pkp,'dname':dname,'rdate':rdate,'del_per_check':del_per_check,'t':'True','timage': 'Image',
                                            'account_details':account_details,'login_obj': login_obj,'user': user, 'profile_pic': profile_pic,
                                            'designations':designations})
    except Exception as e:
        print(e)
        return HttpResponse(e)


def deletereport(request):
    try:
        if request.method == "POST":

            report_id = request.POST['report_id']

            Reportcontent.objects.filter(reportid=report_id).delete()
            Report.objects.filter(pk= report_id).delete()

            return JsonResponse({'data': 'Deleted'})

    except Exception as e:
        print(e)
        return HttpResponse(e)


def delete_users_from_userlist(request):
    if request.method == "POST":
        try:
            user_id = request.POST['userid']
            user_List.objects.filter(Q(admin_id=request.session['user_id'])& Q(user_id=user_id)).delete()

            return JsonResponse({'data':'Updated'})

        except Exception as e:
            return HttpResponse(e)

def detailsmodel(request):
    try:
        if request.method == "POST":
            base_id = request.POST['base_id']

            base_col = Base.objects.filter(id=base_id).values('base_name', 'technical_name','table_type','discription','purpose','bcp','tags')
            print(list(base_col))
            return JsonResponse({'Result': list(base_col)})
    except Exception as e:
        print(e)

def detailsupdate(request):
    try:
        if request.method == "POST":
            basedata = Base.objects.get(id=request.POST['tbl_id'])
            update = 0
            if basedata.base_name != request.POST['base_name']:
                basedata.base_name = request.POST['base_name']
                update += 1

            if basedata.technical_name != request.POST['technical_name']:
                basedata.technical_name = request.POST['technical_name']
                update += 1
            if basedata.table_type != request.POST['ttype']:
                basedata.table_type = request.POST['ttype']
                update += 1
            if basedata.discription != request.POST['discription']:
                basedata.discription = request.POST['discription']
                update += 1
            if basedata.purpose != request.POST['purpose']:
                basedata.purpose = request.POST['purpose']
                update += 1
            if basedata.bcp != request.POST['bcp']:
                basedata.bcp = request.POST['bcp']
                update += 1
            if basedata.tags != request.POST['tagss']:
                basedata.tags = request.POST['tagss']
                update += 1
            if update > 0:
                basedata.save()
        return JsonResponse({'data': 'updated'})



        return JsonResponse({'data':'success'})
    except Exception as e:
        print(e)


# DASHBOARD CHART
def getdashboard(request):
    try:
        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email
        account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
        login_obj = Login.objects.all().exclude(id=request.session['user_id'])
        pro = Profile.objects.filter(log_fk=request.session['user_id'])
        designations=designation.objects.all()
        # Profile pic avilable or not
        profile_pic = ''
        if len(list(pro)) !=0:
            if pro[0].user_image == None:
                profile_pic = 'media/user.jpg'
            else:
                profile_pic = pro[0].user_image.url
        else:
            profile_pic = 'media/user.jpg'

        sub_tbl = Group_model_secondary.objects.all()
        tmp_menu_pk = []
        for item in sub_tbl:
            tmp_menu_pk.append(item.secondary_tables_id)
        menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

        return render(request,'dashboard.html',{'menus':menus,'profile_pic': profile_pic,'pro': pro,'user':user,
                                                'account_details':account_details,'login_obj': login_obj,'designations':designations})
    except Exception as e:
        print(e)

def create_chart(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email

            basedetails_x = Basedetails.objects.filter(bc_fk=request.POST['x_axis']).values('c_v')
            print(basedetails_x)
            basedetails_y= Basedetails.objects.filter(bc_fk=request.POST['yaxis']).values('c_v')


            return JsonResponse({'x_axis':list(basedetails_x),'y_axis':list(basedetails_y)})
        except Exception as e:
            print(e)
            return HttpResponse(e)


def group_models(request):
    user = Login.objects.get(id=request.session['user_id'])
    user_email = user.email
    account_details=Login.objects.filter(id=request.session['user_id']).values('company_name','account_type')
    login_obj = Login.objects.all().exclude(id=request.session['user_id'])
    pro = Profile.objects.filter(log_fk=request.session['user_id'])
    designations=designation.objects.all()
    sec_menus=Base.objects.filter(Q(created_by=user_email)).values('base_name','pk')
    group_names=Group_model_primary.objects.filter(created_users_email=user_email).values('Group_name','pk')
    # Profile pic avilable or not
    profile_pic = ''
    if len(list(pro)) !=0:
        if pro[0].user_image == None:
            profile_pic = 'media/user.jpg'
        else:
            profile_pic = pro[0].user_image.url
    else:
        profile_pic = 'media/user.jpg'

    sub_tbl = Group_model_secondary.objects.all()
    tmp_menu_pk = []
    for item in sub_tbl:
        tmp_menu_pk.append(item.secondary_tables_id)
    menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

    if Group_model_primary.objects.filter(created_users_id=request.session['user_id']).count() > 0:
        primary_tbl = Group_model_primary.objects.filter(created_users_id=request.session['user_id']).\
            values('pk', 'table_id_primary', 'created_users_id', 'Group_name', 'tables_name_primary',
                   'created_users_email')

        primary = []
        secondary = []
        for item in primary_tbl:
            print("****************************")
            print(item['table_id_primary'])
            secondary_tbl = Group_model_secondary.objects.filter(primary_table_fk=item['pk']).\
                values('pk', 'secondary_tables_id', 'secondary_tables_name')

            main_dict = {'master_tbl': item['tables_name_primary'], 'p_id': item['table_id_primary'],
                         'c_u_id':item['created_users_id'], 'name': item['Group_name'], 'pk': item['pk'] ,
                         'total': len(list(secondary_tbl)), 'c_email':item['created_users_email']}

            if len(list(secondary_tbl)) > 0:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                for x in secondary_tbl:
                    dic = {'master_id': item['pk'], 'secndary_tbl': x['secondary_tables_name'],
                           's_id': x['secondary_tables_id'], 's_pk': x['pk']}
                    secondary.append(dic)

            primary.append(main_dict)

        print(primary)
        print(secondary)

        return render(request, 'Group_model.html', {'menus': menus, 'primary': primary, 'secondary': secondary,'account_details':account_details,
                                                    'login_obj': login_obj,'user': user, 'profile_pic': profile_pic,'designations':designations,
                                                    'group_names':group_names,'sec_menus':sec_menus,})
    else:
        return render(request, 'Group_model.html', {'menus': menus,'account_details':account_details,'login_obj': login_obj,
                                                    'user': user, 'profile_pic': profile_pic,'designations':designations,'group_names':group_names,'sec_menus':sec_menus,})


def Create_tbl_group(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.session['user_id'])
            user_email = user.email

            group_name = request.POST['group_name'].upper()
            primary_tbl_id = request.POST['primary_tbl_id']
            secondry_tbl_id = request.POST.getlist('secondry_tbl_id[]')

            if Group_model_primary.objects.filter(Q(created_users_id=request.session['user_id']) & Q(Group_name=group_name) & Q(table_id_primary=primary_tbl_id)).count() > 0:
                pass
            else:
                print(group_name)
                print(primary_tbl_id)
                data = Base.objects.get(pk=primary_tbl_id)
                Group_model_primary.objects.create(table_id_primary=primary_tbl_id,
                                                   created_users_id=request.session['user_id'], Group_name=group_name,
                                                   tables_name_primary=data.base_name, created_users_email=user_email)
                print("##############################")
                primary_data = Group_model_primary.objects.\
                    filter(Q(Group_name=group_name) & Q(created_users_id=request.session['user_id'])).values('pk')
                print("**********************************")
                print(primary_data)

                for item in secondry_tbl_id:
                    print(item)
                    data = Base.objects.get(pk=item)
                    print(data)
                    Group_model_secondary.objects.create(secondary_tables_id=item, secondary_tables_name=data.base_name,
                                                         primary_table_fk=primary_data[0]['pk'])
                    return JsonResponse({'data':'success'})
        except Exception as e:
            return HttpResponse(e)



def delete_secondry_tbl(request):
    if request.method == "POST":
        try:
            tbl_id = request.POST['tbl_id']
            data = Group_model_secondary.objects.get(pk=tbl_id)
            data_count = Group_model_secondary.objects.filter(primary_table_fk=data.primary_table_fk).count()
            if data_count > 1:
                Group_model_secondary.objects.filter(pk=tbl_id).delete()
            else:
                Group_model_primary.objects.filter(pk=data.primary_table_fk).delete()
                Group_model_secondary.objects.filter(pk=tbl_id).delete()
        except Exception as e:
            return HttpResponse(e)


def additional_table(request):
    if request.method == "POST":
        try:
            table_id = int(request.POST['table_id'])
            col_val_names_sub_table = request.POST['col_val_names_sub_table'].strip()
            col_val_id_sub_table = request.POST['col_val_id_sub_table']

            print("col_val_names_sub_table : " + str(col_val_names_sub_table))

            column_values_group = []
            colum_values_id_group = []
            column_row_val_group = []
            column_type_group = []
            alls_group = Basecolumns.objects.filter(base_fk=table_id).values('base_name', 'c_name', 'base_fk', 'pk',
                                                                             'd_type')
            data_for_filter = Basedetails.objects.filter(pk=col_val_id_sub_table).values('bc_fk', 'c_v')

            data_for_filter_cols = Basecolumns.objects.filter(pk=data_for_filter[0]['bc_fk']).values('c_name')
            comman_col_name = 'Uknown'
            comman_col_id = 0
            for item in alls_group:
                if item['c_name'] == data_for_filter_cols[0]['c_name']:
                    comman_col_name = item['c_name']
                    comman_col_id = item['pk']

            print("**********************************************************")
            print("comman_col_name : " + str(comman_col_name))
            print("comman_col_id : " + str(comman_col_id))


            # FOR STORING COLUMNS PRIMARY KEY
            tmp_group = []

            # filtering columns primary key
            for x in alls_group:
                tmp_group.append(x['pk'])

            # Fetching values related to column
            querysets_group = Basedetails.objects.filter(bc_fk__in=tmp_group).values('c_v', 'bc_fk', 'pk', 'row_num').\
                order_by('row_num', 'bc_fk')
            tmp_row = []
            for k in querysets_group:
                tmp_row.append(k['row_num'])

            max_row = 0
            if len(tmp_row) > 0:
                max_row = max(tmp_row)

            print("max row : " + str(max_row))
            for p in range(1, max_row+1):
                tmp_values_group = []
                tmp_values_id_group = []
                tmp_row_val_group = []
                tmp_bck_val_group = []
                for y in querysets_group:
                    if int(y['row_num']) == p:
                        tmp_values_group.append(y['c_v'])
                        tmp_values_id_group.append(y['pk'])
                        tmp_row_val_group.append(y['row_num'])
                        tmp_bck_val_group.append(y['bc_fk'])
                print(tmp_values_group)
                print(tmp_values_id_group)
                print(tmp_bck_val_group)
                print("###############################")
                check_proxy = False
                for f in range(0, len(tmp_bck_val_group)):
                    if tmp_bck_val_group[f] == comman_col_id and tmp_values_group[f] == col_val_names_sub_table:
                        check_proxy = True
                        print("&&&&&&&&&&&&&&&&&&&&&")
                if check_proxy:
                    for s in querysets_group:
                        if int(s['row_num']) == p:
                            column_values_group.append(s['c_v'])
                            colum_values_id_group.append(s['pk'])
                            column_row_val_group.append(s['row_num'])
                            tmp_type = Basecolumns.objects.get(pk=s['bc_fk'])
                            column_type_group.append(tmp_type.d_type)

            additional_tbls = list(zip(column_values_group, colum_values_id_group, column_row_val_group, column_type_group))
            return JsonResponse({"Details": additional_tbls, "Cols": list(alls_group), 'max_row': max_row})

        except Exception as e:
            return HttpResponse(e)


# USER ACCOUNT MAINTANANCE
def fetch_user_role(request):
    if request.method == "POST":
        try:
            user = Login.objects.get(id=request.POST['user'])
            role=user.role

            return JsonResponse({'Result':role})
        except Exception as e:
            print(e)
            return HttpResponse(e)

def remove_user_account(request):
    if request.method == "POST":
        try:
            Login.objects.filter(id=request.POST['user']).delete()


            return JsonResponse({'data':'success'})
        except Exception as e:
            print(e)
            return HttpResponse(e)

def edit_tblcol(request):
    try:
        if request.method == "POST":
            base_id = request.POST['base_id']

            base_col = Basecolumns.objects.filter(base_fk=base_id).values( 'c_name','d_type','d_size','t_name','pk','nul_type')
            print(list(base_col))
            return JsonResponse({'Result': list(base_col)})
    except Exception as e:
        print(e)
#   TO CREATE PROFILE IN USERSLIST
def create_profle_users(request):
    try:
        if request.method == "POST":
            profile = request.POST['profile']
            print(profile)
            if designation.objects.filter(Q(profile=profile)&Q(created_by=request.session['user_id'])).count() == 0:
                if profile !='':
                    designation.objects.create(profile=profile,created_by=request.session['user_id'])
            else:
                messages.success(request, 'profile exist')
            return JsonResponse({'data':'success'})
    except Exception as e:
        print(e)
#TO FETCH GROUP DETAILS
def Group_update_fetch(request):
    try:
        if request.method == "POST":
            group_id = request.POST['group_id']
            print(group_id)
            primary_tbl  = Group_model_primary.objects.filter(Group_name=group_id).values('table_id_primary','pk','tables_name_primary')
            primaryid    = primary_tbl[0]['pk']
            secondary_tbl= Group_model_secondary.objects.filter(primary_table_fk=primaryid).values('secondary_tables_id','secondary_tables_name','pk')
            return JsonResponse({'primary_tbl':list(primary_tbl),'secondary_tbl':list(secondary_tbl)})
    except Exception as e:
        print(e)

def Group_update(request):
    try:
        if request.method == "POST":
            group_id = request.POST['group_id']
            primary_tbl_id = request.POST['primary_tbl_id']
            secondary_table_id = request.POST.getlist('secondary_table_id[]')
            print(group_id)
            print('secondary_table_id')
            print(secondary_table_id)
            if Group_model_primary.objects.filter(pk=group_id).count() >0:
                primary_tbl  = Group_model_primary.objects.filter(pk=group_id).values('table_id_primary','pk','tables_name_primary')
                primaryid    = primary_tbl[0]['pk']

                if primary_tbl[0]['table_id_primary'] !=primary_tbl_id:
                    table_name=Base.objects.get(id=primary_tbl_id)
                    table_name=table_name.base_name
                    Group_model_primary.objects.filter(pk=group_id).update(table_id_primary=primary_tbl_id,tables_name_primary=table_name)

                Group_model_secondary.objects.filter(primary_table_fk=primaryid).delete()
                for x in secondary_table_id:
                    sec_id=int(x)
                    print(sec_id)
                    table_name=Base.objects.get(id=sec_id)
                    table_name=table_name.base_name
                    Group_model_secondary.objects.create(secondary_tables_id=sec_id,secondary_tables_name=table_name,primary_table_fk=primaryid)



            return JsonResponse({'data':'success'})
    except Exception as e:
        print(e)


# Fetching Columns of table based on table id for column properties edit
def col_property_edit(request):
    if request.method == "POST":
        try:
            table_id = request.POST['table']
            data = Basecolumns.objects.filter(Q(base_fk=table_id) & ~Q(d_type='Calc')).\
                values('pk', 'c_name', 'd_type', 't_name', 'd_size', 'nul_type')
            print("Columns of table " + str(table_id) + "is :- ")
            print(list(data))
            return JsonResponse({'Status': True, 'Data': list(data)})
        except Exception as e:
            return JsonResponse({'Status': False})


def edit_column_property(request):
    if request.method == "POST":
        try:
            login_id = Login.objects.get(id=request.session['user_id'])
            login_user = login_id.email

            colname = request.POST['colname']
            type_d = request.POST['type_d']
            valnul = request.POST['v_null']
            col_siz = request.POST['col_size']
            tech_nam = request.POST['tech_namee']
            fk = request.POST['fk']
            id = request.POST['id']

            createdby = login_id.email
            Basecolumns.objects.filter(pk=id).update(c_name=colname, d_type=type_d, d_size=col_siz,
                                                     t_name=tech_nam, nul_type=valnul)
            return JsonResponse({'Status': True})
        except Exception as e:
            return JsonResponse({'Status': False, 'Error': e})


# displaying user details to Administer
def admin_user_management(request):
    try:
        user = Login.objects.get(id=request.session['user_id'])
        user_email = user.email

        account_details = Login.objects.filter(id=request.session['user_id']).values('company_name', 'account_type')
        designations = designation.objects.all()
        sub_tbl = Group_model_secondary.objects.all()
        tmp_menu_pk = []
        for item in sub_tbl:
            tmp_menu_pk.append(item.secondary_tables_id)

        menus = Base.objects.filter(Q(created_by=user_email) & ~Q(pk__in=tmp_menu_pk))

        login_obj = Login.objects.all().exclude(id=request.session['user_id'])

        # FETCHING USER DETAILS FROM USER LIST TABLE
        permissions_list = user_List.objects.filter(user_id=user_email).values('table_id')
        permitted_tables = []
        for item in permissions_list:
            permitted_tables.append(item['table_id'])
        permitted_tables = Base.objects.filter(pk__in=permitted_tables).values('pk', 'base_name')

        pro = Profile.objects.filter(log_fk=request.session['user_id'])
        # Profile pic available or not
        profile_pic = ''
        if len(list(pro)) != 0:
            if pro[0].user_image == None:
                profile_pic = 'media/user.jpg'
            else:
                profile_pic = pro[0].user_image.url
        else:
            profile_pic = 'media/user.jpg'
        """
        nti_msg = notification_Messages.objects.filter(Q(receiver_id=user_email) & Q(status=1)) \
            .values('pk', 'heading', 'message', 'sender_id')
        final_nti_msg = []
        for item in nti_msg:
            if Profile.objects.filter(log_fk=item['sender_id']).count() == 1:
                pic_data = Profile.objects.get(log_fk=item['sender_id'])
                if pic_data.user_image == None:
                    dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                           'pic': 'media/user.jpg'}
                    final_nti_msg.append(dic)
                else:
                    dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                           'pic': pic_data.user_image.url}
                    final_nti_msg.append(dic)
            else:
                dic = {'pk': item['pk'], 'heading': item['heading'], 'message': item['message'],
                       'pic': 'media/user.jpg'}
                final_nti_msg.append(dic)

        nti_count = len(list(nti_msg))


        """
        # REPORT and permitted report
        tmp_rids = []
        rp = Report.objects.filter(created_by=user_email).values('pk')
        for item in rp:
            tmp_rids.append(item['pk'])
        print(tmp_rids)

        permissions_list = user_List.objects.filter(user_id=user_email).values('role')
        rep_role = []
        for item in permissions_list:
            rep_role.append(item['role'])
        print(rep_role)

        rolse_data = permissions.objects.filter(Q(pk__in=rep_role) & Q(view_report='true')).count()
        if rolse_data >= 1:
            per_rolse_data = permissions.objects.filter(Q(pk__in=rep_role) & Q(view_report='true')).values('pk')
            tmp = []
            for item in per_rolse_data:
                tmp.append(item['pk'])
            r_id = user_List.objects.filter(Q(user_id=user_email) & Q(role__in=tmp)).values('report_id')

            for item in r_id:
                tmp_rids.append(item['report_id'])
            print(tmp_rids)
        reports = Report.objects.filter(pk__in=tmp_rids).values('pk', 'Reportname')

        if request.session.has_key('user_id'):
            if user.profile == 'Administer':
                data = Login.objects.filter(Q(company_name=user.company_name) & ~Q(pk=request.session['user_id']) & Q(account_type='company_individual'))\
                    .values('pk', 'email', 'name', 'role', 'phone', 'is_active')
                tmp_data = user_List.objects.filter(admin_id=request.session['user_id']).values('table_id', 'profile',
                                                                                                'user_id')
                array = []
                for x in tmp_data:
                    array.append(x['table_id'])
                base = Base.objects.filter(pk__in=array).values('pk', 'base_name')
                print(tmp_data)
                return render(request, 'user_management.html', {'data': data, 'T': 'True', 'menus': menus, 'pro': pro,
                                                                'permitted_tables': permitted_tables, 'status': 'True',
                                                                'login_obj': login_obj, 'user': user,
                                                                'profile_pic': profile_pic, 'reports': reports,
                                                                'account_details': account_details, 'base': base,
                                                                'designations': designations, 'tmp_data': tmp_data})
            else:
                return render(request, 'user_management.html', { 'menus': menus, 'pro': pro, 'status': 'False',
                                                                 'data':'No Records Available', 'T': 'True',
                                                                 'permitted_tables': permitted_tables,
                                                                 'login_obj': login_obj, 'user': user,
                                                                 'profile_pic': profile_pic, 'reports': reports,
                                                                 'account_details': account_details,
                                                                 'designations': designations})

    except Exception as e:
        return JsonResponse({'Status': False, 'Error': e})


# deactivate users account
def disable_user_account(request):
    if request.method == "POST":
        try:
            admin= Login.objects.get(pk=request.session['user_id'])
            user_name = request.POST['user']
            print(user_name)
            emailid= Login.objects.get(pk=user_name)
            email=emailid.email
            dis_period=request.POST['disable_period']
            print(dis_period)
            if dis_period == '1 Day':
                period_end=datetime.today().date()+timedelta(days=1)
            elif dis_period == '1 Week':
                period_end=datetime.today().date()+timedelta(days=7)
            elif dis_period == '1 Month':
                period_end=datetime.today().date()+timedelta(days=30)
            elif dis_period == '1 Year':
                period_end=datetime.today().date()+timedelta(days=365)
            print(period_end)
            Login.objects.filter(pk=user_name).update(is_disabled='true',disable_period=dis_period,disable_period_end=period_end)
            email_subject = 'Account Deactivated'
            message = render_to_string('deactivate_account.html', {
                'user': emailid,
                'admin':admin,
                'dis_period':dis_period,
                 })
            to_email = email
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()

            return JsonResponse({'data':'success'})

        except Exception as e:
            return HttpResponse(e)

#TO FETCH USER ACCOUNT DETAILS
def fetch_update_user(request):
    try:
        if request.method == "POST":
            sel_user = request.POST['sel_user']
            print(sel_user)
            user_data=Login.objects.filter(id=sel_user).values('name','phone','email','role')
            print(user_data)

            return JsonResponse({'user_data':list(user_data)})
    except Exception as e:
        print(e)

def update_user_account(request):
    try:
        if request.method == "POST":
            sel_user = request.POST['sel_user']
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST['phone']
            role = request.POST['role']
            user = Login.objects.get(id=request.session['user_id'])
            email = user.email
            message = email + 'Updated your Profile'
            Login.objects.filter(id=sel_user).update(name=name,email=email,phone=phone,role=role)
            notification_Messages.objects.create(sender_id=request.session['user_id'],
                                                            receiver_id=user_email, send_date=datetime.today().date(),
                                                            status=1, heading='Profile Updated', message=message)

            return JsonResponse({'data':updated,'Message': 'User Added Successfully', 'Type': 'success'})
    except Exception as e:
        print(e)
def get_row(request):
    try:
        if request.method =='POST':
            table_id=request.POST['table_id']
            row_num =request.POST['mx']
            relation=request.POST.getlist('rr[]')
            print(relation)

            r_values=Basedetails.objects.filter(Q(row_num=row_num) & Q(bc_fk__in=relation)).values('c_v','pk')
            print(r_values)


            return JsonResponse({'data':list(r_values)})
    except Exception as e:
        print(e)