from django.contrib import auth as django_auth
import base64
import hashlib
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from sign.models import Event, Guest
import time
import json
from Crypto.Cipher import AES


'''
get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
request.META 是一个 Python 字典， 包含了所有本次 HTTP 请求的 Header 信息， 比如用户认证、 IP 地址
和用户 Agent（通常是浏览器的名称和版本号） 等。
HTTP_AUTHORIZATION 用于获取 HTTP authorization。
然后， 得到的数据是这样的： Basic YWRtaW46YWRtaW4xMjM0NTY=
auth = get_http_auth.split()
通过 split()方法将其拆分成 list。 拆分后的数据是这样的： ['Basic', 'YWRtaW46YWRtaW4xMjM0NTY=']
auth_parts = base64.b64decode(auth[1]).decode('iso-8859-1').partition(':')
取出 list 中的加密串， 通过 base64 对加密串进行解码。 得到的数据是： ('admin', ':', 'admin123456')
执行到这一行， 如果获取不到 Auth 信息， 将会抛 IndexError 异常， 通过 try...except...进行异常捕捉， 如果捕捉到异常将返回“null” 。
userid, password = auth_parts[0], auth_parts[2]
最后， 取出元组中对应的用户 id 和密码。 最终于数据： admin admin123456
再接来的处理过程我们就很熟悉了。 调用 Django 的认证模块， 对得到 Auth 信息进行认证。 成功将返回“success” ， 失败则返回“fail” 。
'''
def user_auth(request):
    get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
    auth = get_http_auth.splist()
    try:
        auth_parts = base64.b64decode(auth[1]).decode('iso-8859-1')\
                                                            .partition(':')
    except IndexError:
        return "null"
    userid, password = auth_parts[0], auth_parts[2]
    user = django_auth.authenticate(username=userid, password=password)
    if user is not None and user.is_active:
        django_auth.login(request, user)
        return "success"
    else:
        return "fail"

def get_event_list(request):
    auth_result = user_auth(request)            # 调用认证函数
    if auth_result == "null":
        return JsonResponse({'status': 10011, 'message': 'user auth null'})
    if auth_result == "fail":
        return JsonResponse({'status': 10012, 'message': 'user auth fail'})
    eid = request.GET.get("eid", "")            #发布会 id
    name = request.GET.get("name", "")          #发布会名称
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
首先，通过 POST 方法获取两个参数 time 和 sign 两个参数，并判断它们其中的任一一个为空，则返回“signnull” ，
这个逻辑很好理解。接下来， 是判断时间戳。 需要客户端获取一个“当前时间戳” ， 取当前的时间。 （例如， 1466830935）
Python3 生成的的时间戳精度太高， 我们只需要小数点前面的 10 位即可。 所以， 使用 split()函数截取小
数点前面的时间。同样， 当服务器端口拿到客户端传来的时间戳后， 服务器端也需要重新再获取一下当前时间戳。 
如果服务器端的当前时间戳减法去客户端时间戳小于 60， 说明这个接口的请求时间是离现在最近的 60 秒之内。 
那么允许接口访问， 如果超过 60 秒， 则返回“timeout” 。
这样就要求请求的客户端不断的获取当前戳作为接口参来访问接口。 所以， 一直用固定的参数访问接口是无效的。
关于是签名参数的生成。 需要将 api_key（密钥字符串： “&Guest-Bugmaster” ） 和客户端发来的时间戳，
两者拼接成一个新的字符串。 并且通过 MD5 对其进行加密。 从而将加密后的字符串作为 sign 的字段的参数。
服务器端以同样的规则来生成这样一个加密后的字符串， 从而比较这个串是否相等， 如果相等说明签名
验证通过； 如果不相等， 则返回“sign fail” 。
'''
# 用户签名+时间戳
def user_sign(request):
    client_time = request.POST.get('time', '')
    client_sign = request.POST.get('sign', '')
    if client_time == '' or client_sign == '':
        return "sign null"
    # 服务器时间
    now_time = time.time() # 1466426831
    server_time = str(now_time).split('.')[0]
    # 获取时间差
    time_difference = int(server_time) - int(client_time)
    if time_difference >= 60 :
        return "timeout"
    # 签名检查
    md5 = hashlib.md5()
    sign_str = client_time + "&Guest-Bugmaster"
    sign_bytes_utf8 = sign_str.encode(encoding="utf-8")
    md5.update(sign_bytes_utf8)
    sever_sign = md5.hexdigest()
    if sever_sign != client_sign:
        return "sign error"
    else:
        return "sign right"

# 添加发布会接口---增加签名+时间戳
def add_event(request):
    sign_result = user_sign(request)  # 调用签名函数
    if sign_result == "sign null":
        return JsonResponse({'status': 10011, 'message': 'user sign null'})
    elif sign_result == "timeout":
        return JsonResponse({'status': 10012, 'message': 'user sign timeout'})
    elif sign_result == "sign error":
        return JsonResponse({'status': 10013, 'message': 'user sign error'})
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
app_key = 'W7v4D60fds2Cmk2U'服务器端与合法客户端约定的密钥 app_key。
if request.method == 'POST':
data = request.POST.get("data", "")
判断客户端请求是否为 POST， 通过 POST.get()方法接收 data 参数。
decode = decryptAES(data, app_key)
调用解密函数 decryptAES() ， 传参加密字符串和 app_key。
def decryptAES(src, key):
"""解析 AES 密文 """
src = decryptBase64(src)
iv = b"1172311105789011"
cryptor = AES.new(key, AES.MODE_CBC, iv)
text = cryptor.decrypt(src).decode()
return unpad(text)
首先， 调用 decryptBase64()方法， 将 Base64 加密字符串解密为 AES 加密字符串。 然后， 通过 decrypt()对 AES 加密串进行解密。
def decryptBase64(src):
return base64.urlsafe_b64decode(src)
对 Base64 字符串解密。
BS = 16
unpad = lambda s : s[0: - ord(s[-1])]
最后， 通过 upad 匿名函数对字符串的长度还原。 到此， 解密过程结束。
dict_data = json.loads(decode)
return dict_data
将解密后字符串通过 json.loads()方法转化成字典， 并将该字典做为 aes_encryption()函数的返回值。
在获取嘉宾例表的接口中调用 aes_encryption()函数进行 AES 加密字符串解密。
'''
#=======AES 加密算法===============
BS = 16
unpad = lambda s : s[0: - ord(s[-1])]

def decryptBase64(src):
    return base64.urlsafe_b64decode(src)

def decryptAES(src, key):
    """解析 AES 密文"""
    src = decryptBase64(src)
    iv = b"1172311105789011"
    cryptor = AES.new(key, AES.MODE_CBC, iv)
    text = cryptor.decrypt(src).decode()
    return unpad(text)

def aes_encryption(request):
    app_key = 'W7v4D60fds2Cmk2U'
    if request.method == 'POST':
        data = request.POST.get("data", "")
    # 解密
        decode = decryptAES(data, app_key)
    # 转化为字典
        dict_data = json.loads(decode)
        return dict_data


# 嘉宾查询接口----AES 算法
def get_guest_list(request):
    dict_data = aes_encryption(request)
    eid = dict_data['eid']
    phone = dict_data['phone']
    if eid == '':
        return JsonResponse({'status':10021,'message':'eid cannot be empty'})
    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
                return JsonResponse({'status':200, 'message':'success', 'data':datas})
        else:
                return JsonResponse({'status':10022, 'message':'query result is empty'})
    if eid != '' and phone != '':
        guest = {}
        try:
            result = Guest.objects.get(phone=phone,event_id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status':200, 'message':'success', 'data':guest})