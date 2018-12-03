from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from sign.models import Event, Guest
from django.db.utils import IntegrityError
import time

'''
通过 POST 请求接收发布会参数： 发布会 id、 标题、 人数、 状态、 地址和时间等参数。
首先， 判断 eid、 name、 limit、 address、 start_time 等字段均不能为空， 否则 JsonResponse()返回相应的状态码和提示。
JsonResponse()是一个非常有用的方法， 它可以直接将字典转化成 Json 格式返回到客户端。
接下来， 判断发布会 id 是否存在， 以及发布会名称（name） 是否存在； 如果存在将返回相应的状态码和提示信息。
再接下来， 判断发布会状态是否为空， 如果为空， 将状态设置为 1（True） 。
最后， 将数据插入到 Event 表， 在插入的过程中如果日期格式错误， 将抛出 ValidationError 异常， 接收该异常并返回相应的状态和提示， 
否则， 插入成功， 返回状态码 200 和“add event success” 的提示。
'''
# 添加发布会接口
def add_event(request):
    eid = request.POST.get('eid', '')              # 发布会 id
    name = request.POST.get('name', '')             # 发布会标题
    limit = request.POST.get('limit', '')            # 限制人数
    status = request.POST.get('status', '')           # 状态
    address = request.POST.get('address', '')          # 地址
    start_time = request.POST.get('start_time', '')     # 发布会时间
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status': 10022, 'message': 'event id already exists'})
    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 10023, 'message': 'event name already exists'})
    if status == '':
        status = 1
    try:
        Event.objects.create(id=eid, name=name, limit=limit, address=address, status=int(status), start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 10024, 'message': error})
    return JsonResponse({'status':200,'message':'add event success'})

'''
通过 GET 请求接收发布会 id 和 name 参数。 两个参数都是可选的。 
首先， 判断当两个参数同时为空， 接口返回状态码 10021， 参数错误。
如果发布会 id 不为空， 优先通过 id 查询， 因为 id 的唯一性， 
所以， 查询结果只会有一条， 将查询结果以 key:value 对的方式存放到定义的 event 字典中， 
并将数据字典作为整个返回字典中 data 对应的值返回。name 查询为模糊查询， 
查询数据可能会有多条， 返回的数据稍显复杂； 首先将查询的每一条数据放到一个字典 event 中， 
再把每一个字典再放到数组 datas 中， 最后再将整个数组做为返回字典中 data 对应的值返回。
'''
# 发布会查询
def get_event_list(request):
    eid = request.GET.get("eid", "") #发布会 id
    name = request.GET.get("name", "") #发布会名称
    if eid == '' and name == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})
    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
        return JsonResponse({'status': 200, 'message': 'success', 'data': event})
    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})

'''
通过 POST 请求接收嘉宾参数： 关联的发布会 id、 姓名、 手机号和邮箱等参数。
首先， 判断 eid、 realname、 phone 等参数均不能为空。
接下来， 判断嘉宾关联的发布会 id 是否存在， 以及关联的发布会状态是否为 True（即 1） ， 如果不存在
或不为 True， 将返回相应的状态码和提示信息。
再接下来的步骤是判断当前时间是否大于发布会时间， 如果大于则说明发布已开始， 或者早已经结束。
那么该发布会就应该不能允许再添加嘉宾。
最后， 插入嘉宾数据， 如果发布会的手机号重复则抛 IntegrityError 异常， 接收该异常并返回相应的状态
码和提示信息。 如果添加成功， 则返回状态码 200 和“add guest success” 的提示。
'''
# 添加嘉宾接口
def add_guest(request):
    eid = request.POST.get('eid', '')                 # 关联发布会 id
    realname = request.POST.get('realname', '')       # 姓名
    phone = request.POST.get('phone', '')             # 手机号
    email = request.POST.get('email', '')             # 邮箱
    if eid =='' or realname == '' or phone == '':
        return JsonResponse({'status': 10021, 'message': 'evlent id null'})
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022, 'message': 'parameter error'})
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023, 'message': 'event status is not available'})
    event_limit = Event.objects.get(id=eid).limit       # 发布会限制人数
    guest_limit = Guest.objects.filter(event=eid)    # 发布会已添加的嘉宾数
    if len(guest_limit) >= event_limit:
        return JsonResponse({'status': 10024, 'message': 'event number is full'})
    event_time = Event.objects.get(id=eid).start_time   # 发布会时间
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime, "%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))
    now_time = str(time.time())                         # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)
    if n_time >= e_time:
        return JsonResponse({'status': 10025, 'message': 'event has started'})
    try:
        Guest.objects.create(realname=realname, phone=int(phone), email=email, sign=0, event=int(eid))
    except IntegrityError:
        return JsonResponse({'status': 10026, 'message': 'the event guest phone number repeat'})
    return JsonResponse({'status': 200, 'message': 'add guest success'})

'''
嘉宾查询接口与发布会查询接口相似， 只是参数与查询条件判断有所不同
'''
# 嘉宾查询接口
def get_guest_list(request):
    eid = request.GET.get("eid", "")            # 关联发布会 id
    phone = request.GET.get("phone", "")        # 嘉宾手机号
    if eid == '':
        return JsonResponse({'status': 10021, 'message': 'eid cannot be empty'})
    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
            return JsonResponse({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})
    if eid != '' and phone != '':
        guest = {}
        try:
            result = Guest.objects.get(phone=phone, event=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': 'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status': 200, 'message': 'success', 'data': guest})

'''
签到接口通过 POST 请求接收发布会 id 和嘉宾手机号。 签到接口的判断条件比较多。
首先， 判断两个参数均不能为空。
接着， 判断发布会 id 是否存在， 以及发布会状态是否为 True， 如果不存在或不为 True， 将返回相应的状态码和提示信息。
再接着， 判断当前时间是否大于发布会时间， 如果大于发布会时间说明发布会已开始， 不允许签到。
然后， 再判断嘉宾的手机号是否存在， 以及嘉宾的手机号与发布会 id 是否为对应关系。 否则返回相应的错误码和提示信息。
最后， 判断该嘉宾的状态是否为已签到， 如果已签到， 返回相应的状态码和提示； 如果未签到修改状态
为已签到， 并返回状态码 200 和“sign success” 的提示。
'''
# 嘉宾签到接口
def user_sign(request):
    eid = request.POST.get('eid', '')                           # 发布会 id
    phone = request.POST.get('phone', '')                       # 嘉宾手机号
    if eid =='' or phone == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022, 'message': 'event id null'})
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023, 'message': 'event status is not available'})
    event_time = Event.objects.get(id=eid).start_time           # 发布会时间
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime, "%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))
    now_time = str(time.time())                                 # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)
    if n_time >= e_time:
        return JsonResponse({'status': 10024, 'message': 'event has started'})
    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status': 10025, 'message': 'user phone null'})
    result = Guest.objects.filter(event=eid, phone=phone)
    if not result:
        return JsonResponse({'status': 10026, 'message': 'user did not participate in the conference'})
    result = Guest.objects.get(event=eid, phone=phone).sign
    if result:
        return JsonResponse({'status': 10027, 'message': 'user has sign in'})
    else:
        Guest.objects.filter(event=eid, phone=phone).update(sign='1')
        return JsonResponse({'status': 200, 'message': 'sign success'})
