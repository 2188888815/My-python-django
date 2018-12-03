from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
# Create your views here.
'''
我们要把这些“窗户” 都关上,只需要在这个函数的前面加上  @login_required
'''

def index(request):
    return render(request,"index.html")

# 登录动作
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)  # 登录
            request.session['user'] = username  # 将 session 信息记录到浏览器
            response = HttpResponseRedirect('/event_manage/')
            return response
        else:
            return render(request,'index.html', {'error': 'username or passworderror!'})
    else:
        return render(request, 'index.html', {'error': 'username or passworderror!'})

# 发布会管理
#@login_required
def event_manage(request):
    username = request.session.get('user', '')
    event_list = Event.objects.all()
    paginator = Paginator(event_list, 2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, "event_manage.html", {"user": username,"events": contacts})

# 发布会名称搜索
#@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get("name", "")
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, "event_manage.html", {"user": username,"events": event_list})

'''
paginator = Paginator(guest_list, 2)
把查询出来的所有嘉宾列表 guest_list 放到 Paginator 类中， 划分每页显示 2 条数据。
page = request.GET.get('page')
通过 GET 请求得到当前要显示第几页的数据。
contacts = paginator.page(page)
获取第 page 页的数据。 如果当前没有页数， 抛 PageNotAnInteger 异常， 返回第一页的数据。 如果超出最
大页数的范围， 抛 EmptyPage 异常， 返回最后一页面的数据。
最终， 将得到的某一页数据返回到嘉宾管理页面上。
'''
# 嘉宾管理
#@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username,"guests": contacts})

#嘉宾名称搜索
#@login_required
def guest_search_name(request):
    username = request.session.get('user', '')
    guest_search_name = request.GET.get('name', '')
    guest_list = Guest.objects.filter(realname__contains=guest_search_name)
    return render(request, "guest_manage.html", {"user": username,"guests": guest_list})

# 签到页面
@login_required
def sign_index(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'sign_index.html', {'event': event})

'''
首先， 查询 Guest 表判断用户输入的手机号是否存在， 如果不存在将提示用户“手机号为空或不存在” 。
然后， 通过手机和发布会 id 两个条件来查询 Guest 表， 如果结果为空将提示用户“该用户未参加此次发布会” 。
最后， 再通过手机号查询 Guest 表， 判断该手机号的签到状态是否为 1， 如果为 1， 表示已经签过到了，
返回用户“已签到” ， 否则， 将提示用户“签到成功！ ” ， 并返回签到用户的信息。
'''
# 签到动作
#@login_required
def sign_index_action(request,event_id):
    event = get_object_or_404(Event, id=event_id)
    phone = request.POST.get('phone','')
    result = Guest.objects.filter(phone = phone)
    if not  result:
        return render(request, 'sign_index.html', {'event': event,'hint': 'phone error.'})
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event,'hint': 'event id or phone error.'})
    result = Guest.objects.get(phone=phone)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event,'hint': "user has sign in."})
    else:
        Guest.objects.filter(phone=phone).update(sign = '1')
        return render(request, 'sign_index.html', {'event': event,'hint':'sign in success!', 'guest': result})

# 退出登录
@login_required
def logout(request):
    auth.logout(request)  # 退出登录
    response = HttpResponseRedirect('/index/')
    return response
