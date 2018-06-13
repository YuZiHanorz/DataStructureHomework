from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from django.conf import settings
from django.contrib import messages

from urllib.request import urlopen
from urllib.error import HTTPError

import json
import os
import ctypes
import requests

#context = {'login_name':'test', 'authority':0, 'style':'1'}
#need to fix context which send login_name and authority to html
#authority 0: not login 1: normal user 2:admin

def getServerSideCookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def cstyle0(request):
    request.session['tmpstyle'] = '0'
    return HttpResponseRedirect(reverse('index'))

def cstyle1(request):
    request.session['tmpstyle'] = '1'
    return HttpResponseRedirect(reverse('index'))

def index(request):
    context = {}
    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    login = getServerSideCookie(request, 'login')
    if login != None:
        messages.success(request, '您好，{}，欢迎回来！'.format(login))
        request.session['login'] = None

    register = getServerSideCookie(request, 'register')
    if register != None:
        name, id = register.split()
        messages.success(request, '您好，{}，欢迎注册！您的用户ID为{}，请牢记。'.format(name, id))
        request.session['register'] = None

    return render(request, 'index.html', context)

def about(request):
    context = {}
    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'About.html', context)

def getip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip

def getCountry(ipAddress):
    try:
        response = urlopen("http://freegeoip.net/json/"+ipAddress).read().decode('utf-8')
    except HTTPError:
        pass
    responseJson = json.loads(response)
    return responseJson.get("country_code")

def uploading(request):
    context = {}
    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'Uploading.html', context)

def login(request):
    context = {}
    userid = getServerSideCookie(request, 'userid', '0')
    userpv = getServerSideCookie(request, 'userpv', '0')

    if userid != '0':
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')

        lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
        dataInput = ctypes.create_string_buffer(' '.join((userid, password)).encode('UTF-8'))
        dataOutput = ctypes.create_string_buffer(10)
        inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
        outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
        lib.userLogin(inputPointer, outputPointer)
        info = dataOutput.value.decode('UTF-8')

        if info == '1':
            request.session['userid'] = userid

            lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
            dataInput = ctypes.create_string_buffer(userid.encode('UTF-8'))
            dataOutput = ctypes.create_string_buffer(1000)
            inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
            outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
            lib.userQueryProfile(inputPointer, outputPointer)
            info = dataOutput.value.decode('UTF-8')
            username, password, emailaddress, phonenumber, userpv = info.split()

            request.session['userpv'] = userpv
            request.session['login'] = username

            return HttpResponseRedirect(reverse('index'))

    context['login_name'] = userid
    context['authority'] = userpv
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'login.html', context)

def signup(request):
    context = {}
    userid = getServerSideCookie(request, 'userid', '0')
    userpv = getServerSideCookie(request, 'userpv', '0')

    if userid != '0':
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        username = request.POST.get('username')
        emailaddress = request.POST.get('emailaddress')
        phonenumber = request.POST.get('phonenumber')
        password = request.POST.get('password')

        lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
        dataInput = ctypes.create_string_buffer(' '.join((username, password, emailaddress, phonenumber)).encode('UTF-8'))
        dataOutput = ctypes.create_string_buffer(10)
        inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
        outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
        lib.userRegister(inputPointer, outputPointer)
        info = dataOutput.value.decode('UTF-8')

        if info != '0':
            request.session['register'] = ' '.join((username, info))
            return HttpResponseRedirect(reverse('index'))

    context['login_name'] = userid
    context['authority'] = userpv
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'signup.html', context)

def signupadmin(request):
    #print(getip(request))
    #print(getCountry('203.78.6.5'))
    context = {}
    userid = getServerSideCookie(request, 'userid', '0')
    userpv = getServerSideCookie(request, 'userpv', '0')

    if request.method == 'POST':
        username = request.POST.get('username')
        emailaddress = request.POST.get('emailaddress')
        phonenumber = request.POST.get('phonenumber')
        password = request.POST.get('password')

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }

        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            print(result['success'])
        except BaseException:
            result = {'success':'true'}

        if result['success'] == 'true':
            tmpip = getip(request)
            Country_code = getCountry(tmpip)

            #print(tmpip)
            if tmpip == '127.0.0.1' or Country_code == 'CN':
                lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
                dataInput = ctypes.create_string_buffer(' '.join((username, password, emailaddress, phonenumber)).encode('UTF-8'))
                dataOutput = ctypes.create_string_buffer(1000)
                inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
                outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
                lib.userRegister(inputPointer, outputPointer)
                info = dataOutput.value.decode('UTF-8')

                if info != '-1':
                    return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, 'IP unacceptable')
        else:
            messages.error(request, '请正确填写验证码。')
    context['login_name'] = userid
    context['authority'] = userpv
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'Signupadmin.html', context)

def user_logout(request):
    request.session['userid'] = None
    request.session['userpv'] = None
    request.session['tmpstyle'] = None
    return HttpResponseRedirect(reverse('index'))

def cinfo(request):
    context = {}
    userid = getServerSideCookie(request, 'userid', '0')
    userpv = getServerSideCookie(request, 'userpv', '0')

    if userid == None:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':

        email = request.POST.get('email')
        name = request.POST.get('name')
        oldpwd = request.POST.get('oldpwd')
        pwd = request.POST.get('pwd')
        phone = request.POST.get('phone')

        password = oldpwd
        lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
        dataInput = ctypes.create_string_buffer(' '.join((userid, password)).encode('UTF-8'))
        dataOutput = ctypes.create_string_buffer(10)
        inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
        outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
        lib.userLogin(inputPointer, outputPointer)
        info = dataOutput.value.decode('UTF-8')

        if info == '1':

            if pwd == '':
                pwd = oldpwd

            lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
            dataInput = ctypes.create_string_buffer(' '.join((userid, name, pwd, email, phone)).encode('UTF-8'))
            dataOutput = ctypes.create_string_buffer(10)
            inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
            outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
            lib.userModifyProfile(inputPointer, outputPointer)
            info = dataOutput.value.decode('UTF-8')

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'ChangeInfo.html', context)

def privilege(request):
    context = {}
    userid = getServerSideCookie(request, 'userid', '0')
    userpv = getServerSideCookie(request, 'userpv', '0')

    if userpv != '2':
        return HttpResponseRedirect(reverse('index'))

    context['login_name'] = userid
    context['authority'] = userpv
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    if request.method == 'POST':
        opuserid = request.POST.get('userid')

        lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
        dataInput = ctypes.create_string_buffer(' '.join((userid, opuserid, '2')).encode('UTF-8'))
        dataOutput = ctypes.create_string_buffer(1000)
        inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
        outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
        lib.userModifyPrivilege(inputPointer, outputPointer)
        info = dataOutput.value.decode('UTF-8')

        if info == '1':
            return HttpResponseRedirect(reverse('index'))

    return render(request, 'Privilege.html', context)

def showinfo(request):
    context = {}
    userid = getServerSideCookie(request, 'userid', '0')
    userpv = getServerSideCookie(request, 'userpv', '0')

    if userid == None:
        return HttpResponseRedirect(reverse('index'))

    context['login_name'] = userid
    context['authority'] = userpv
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
    dataInput = ctypes.create_string_buffer(userid.encode('UTF-8'))
    dataOutput = ctypes.create_string_buffer(1000)
    inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
    outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
    lib.userQueryProfile(inputPointer, outputPointer)
    info = dataOutput.value.decode('UTF-8')

    print(info)
    username, password, emailaddress, phonenumber, userpv = info.split()

    context['email'] = emailaddress
    context['phone'] = phonenumber
    context['name'] = username

    return render(request, 'ShowInfo.html', context)

def page_not_found(request):
    context = {}
    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'Error.html', context)

def page_error(request):
    context = {}
    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    return render(request, 'Error.html', context)
