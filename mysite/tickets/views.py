from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.template import RequestContext
from django.contrib import messages

from django.utils.translation import ugettext as _

import os
import ctypes

def getServerSideCookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def index(request):
    context = {}
    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    loginFirst = getServerSideCookie(request, 'loginFirst')
    if loginFirst != None:
        messages.error(request, _('Hello, please log in first.'))
        #msg = _('您好，请先登录。')
        #context['msg'] = msg
        request.session['loginFirst'] = None

    addTicket = getServerSideCookie(request, 'addTicket')
    print('session here:', addTicket)
    if addTicket != None:
        #messages.success(request, '您已成功购票。')
        msg = _('You have successfully buy tickets.')
        context['msg'] = msg
        request.session['addTicket'] = None

    if request.method == 'POST':

        trainid = request.POST.get('trainid')
        if trainid != None:
            userid = context['login_name']
            num_buy = request.POST.get('num_buy')
            fr = request.POST.get('trainfr')
            to = request.POST.get('trainto')
            date = request.POST.get('date')
            class_name = request.POST.get('class_name')

            print('user?', userid)

            if userid == '0':
                request.session['loginFirst'] = '1'

                tmp = getServerSideCookie(request, 'loginFirst')

                print('login first', tmp)
                # login first
                return HttpResponseRedirect(reverse('train_seek'))

            print('Buying:', ' '.join((userid, num_buy, trainid, fr, to, date, class_name)))

            lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
            dataInput = ctypes.create_string_buffer(' '.join((userid, num_buy, trainid, fr, to, date, class_name)).encode('UTF-8'))
            dataOutput = ctypes.create_string_buffer(10)
            inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
            outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
            lib.buyTicket(inputPointer, outputPointer)
            info = dataOutput.value.decode('UTF-8')

            request.session['addTicket'] = '1'
            print('session set to addTicket')

            return HttpResponseRedirect(reverse('train_seek'))


        context['asked'] = True

        fs = request.POST.get('from')
        ts = request.POST.get('to')
        date = request.POST.get('date')
        context['fs'] = fs
        context['ts'] = ts
        context['date'] = date
        ask = ' '.join((fs, ts, date, 'GCDZTK'))

        lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
        dataInput = ctypes.create_string_buffer(ask.encode('UTF-8'))
        dataOutput = ctypes.create_string_buffer(50000)
        inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
        outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
        lib.queryTicket(inputPointer, outputPointer)
        info = dataOutput.value.decode('UTF-8')

        print(ask, info)

        col = 0

        if info != '0':

            Trains = []
            for item in info.split('|'):
                ticket = item.split()
                x = []
                x.append(ticket[0])
                x.append(ticket[1])
                x.append(ticket[2])
                x.append(ticket[4])
                x.append(ticket[5])
                x.append(ticket[7])
                class_price = []
                p = 8
                while 1:
                    if p == len(ticket):
                        break
                    price = []
                    price.append(ticket[p])
                    price.append(ticket[p + 1])
                    price.append(str(round(float(ticket[p + 2]))))
                    p += 3
                    col += 1
                    class_price.append((col, price))
                x.append(class_price)
                Trains.append(x)
            print(Trains)
            context['Trains'] = Trains

        transfer = request.POST.get('transfer')
        if transfer == 'yes':
            context['transfer'] = '1'

            lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
            dataInput = ctypes.create_string_buffer(ask.encode('UTF-8'))
            dataOutput = ctypes.create_string_buffer(50000)
            inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
            outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
            lib.queryTransfer(inputPointer, outputPointer)
            info = dataOutput.value.decode('UTF-8')

            print(info)

            if info != '0':
                Trains1 = []
                for item in info.split('|'):
                    ticket = item.split()
                    x = []
                    x.append(ticket[0])
                    x.append(ticket[1])
                    x.append(ticket[2])
                    x.append(ticket[4])
                    x.append(ticket[5])
                    x.append(ticket[7])
                    class_price = []
                    p = 8
                    while 1:
                        if p == len(ticket):
                            break
                        price = []
                        price.append(ticket[p])
                        price.append(ticket[p + 1])
                        price.append(str(round(float(ticket[p + 2]))))
                        p += 3
                        col += 1
                        class_price.append((col, price))
                    x.append(class_price)
                    Trains1.append(x)
                print(Trains1)
                context['Trains1'] = Trains1

    return render(request, 'SeekTickets.html', context)

def buy_history(request):
    context = {}

    context['login_name'] = getServerSideCookie(request, 'userid', '0')
    context['authority'] = getServerSideCookie(request, 'userpv', '0')
    context['style'] = getServerSideCookie(request, 'tmpstyle', '1')

    loginFirst = getServerSideCookie(request, 'loginFirst')
    if loginFirst != None:
        #messages.success(request, '您好，请先登录。')
        messages.error(request, _('Hello, please log in first.'))
        request.session['loginFirst'] = None

    delTicket = getServerSideCookie(request, 'delTicket')
    if delTicket != None:
        #messages.success(request, '您已成功退票。')
        msg = _('You have successfully return the tickets.')
        context['msg'] = msg
        request.session['delTicket'] = None

    if request.method == 'POST':
        userid = context['login_name']
        date = request.POST.get('date')

        trainid = request.POST.get('trainid')
        if trainid != None:
            print('returning')

            userid = context['login_name']
            num_ret = request.POST.get('num_ret')
            fr = request.POST.get('trainfr')
            to = request.POST.get('trainto')
            date = request.POST.get('date')
            class_name = request.POST.get('class_name')

            lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
            dataInput = ctypes.create_string_buffer(' '.join((userid, num_ret, trainid, fr, to, date, class_name)).encode('UTF-8'))
            dataOutput = ctypes.create_string_buffer(10)
            inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
            outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
            lib.refundTicket(inputPointer, outputPointer)
            info = dataOutput.value.decode('UTF-8')

            print(info)

            if info == '1':
                request.session['delTicket'] = '1'
                # return ticket
                return HttpResponseRedirect(reverse('buy_history'))

        if userid == '0':
            request.session['loginFirst'] = '1'
            # login first
            return HttpResponseRedirect(reverse('buy_history'))

        lib = ctypes.cdll.LoadLibrary('./lib/crsystem/libcr.so')
        dataInput = ctypes.create_string_buffer(' '.join((userid, date, 'GCDZTK')).encode('UTF-8'))
        dataOutput = ctypes.create_string_buffer(50000)
        inputPointer = (ctypes.c_char_p)(ctypes.addressof(dataInput))
        outputPointer = (ctypes.c_char_p)(ctypes.addressof(dataOutput))
        lib.queryOrder(inputPointer, outputPointer)
        info = dataOutput.value.decode('UTF-8')

        if info == '0':
            return render(request, "buyhistory.html", context)

        print(info)

        col = 0

        Historys = []
        for item in info.split('|'):
            ticket = item.split()
            x = []
            x.append(ticket[0])
            x.append(ticket[1])
            x.append(ticket[2])
            x.append(ticket[4])
            x.append(ticket[5])
            x.append(ticket[7])
            class_price = []
            p = 8
            while 1:
                if p == len(ticket):
                    break
                price = []
                price.append(ticket[p])
                price.append(ticket[p + 1])
                price.append(str(round(float(ticket[p + 2]))))
                p += 3
                col += 1
                class_price.append((col, price))
            x.append(class_price)
            Historys.append(x)
        print(Historys)
        context['Historys'] = Historys
        context['date'] = date

    return render(request, "buyhistory.html", context)
