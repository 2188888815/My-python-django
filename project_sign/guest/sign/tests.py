
from django.test import TestCase
from sign.models import Event,Guest
from django.test import Client
from django.contrib.auth.models import User
from datetime import datetime

# Create your tests here.

'''
首先， 创建 ModelTest 类， 继承 django.test 的 TestCase 测试类。
然后， 在 setUp()初始化方法中， 创建一条发布会和嘉宾数据。
最后， 通过 test_event_models()和 test_guest_models()测试方法， 分别查询两张表的数据， 断言表中的数据是否正确。
'''
#发布会和嘉宾数据
class ModelTest(TestCase):
    def setUp(self):
        Event.objects.create(id=1, name="oneplus 3 event", status=True, limit=2000, address='shenzhen', start_time='2016-08-31 02:18:22')
        Guest.objects.create(id=1, event=1, realname='alen', phone='13711001101', email='alen@mail.com', sign=False)
    def test_event_models(self):
        result = Event.objects.get(name="oneplus 3 event")
        self.assertEqual(result.address, "shenzhen")
        self.assertTrue(result.status)
    def test_guest_models(self):
        result = Guest.objects.get(phone='13711001101')
        self.assertEqual(result.realname, "alen")
        self.assertFalse(result.sign)

'''
client.get()方法从 TestCase 父类继承而来， 用于请求一个路径， 
assertEqual()服务器对客户端的应答是否为 200， assertTemplateUsed()断言是否用给定的是 index.html 模版响应。
'''
#测试 index 登录首页
class IndexPageTest(TestCase):
    ''' 测试 index 登录首页 '''
    def test_index_page_renders_index_template(self):
        ''' 测试 index 视图 '''
        response = self.client.get('http://127.0.0.1:8000/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

'''
在 setUp()初始化方法中， 调用 User.objects.create_user()创建登录用户数据。Client()类提供的 get()和 post()
方法可以模式 GET/POST 请求。“/login_action/” 为用户登录的路径。
{'username':'admin','password':'admin123456'} 字典中的内容为用户登录的用户名密码。
前两条例分别为用户名/密码为空， 和用户名/密码错误。 assertIn()断言在返回的 HTML 中包含“usernameor password error!” 提示。
当用例中输入了正确的用户名和密码（admin/admin123456）， 为什么 HTTP 返回的结果是 302 而不是 200呢？
这是因为在 login_action 视图函数中， 当用户登录验证成功后， 通过 HttpResponseRedirect('/event_manage/')
跳转到了发布会管理视图， 这是一个重定向， 所以 HTTP 返回码是 302。
'''
#测试登录函数
class LoginActionTest(TestCase):
    ''' 测试登录函数'''
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        self.c = Client()
    def test_login_action_username_password_null(self):
        ''' 用户名密码为空 '''
        test_data = {'username': '', 'password': ''}
        response = self.c.post('http://127.0.0.1:8000/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"username or passworderror!", response.content)
    def test_login_action_username_password_error(self):
        ''' 用户名密码错误 '''
        test_data = {'username': 'abc', 'password': '123'}
        response = self.c.post('http://127.0.0.1:8000/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"username or passworderror!", response.content)
    def test_login_action_success(self):
        ''' 登录成功 '''
        test_data = {'username': 'admin', 'password': 'admin123456'}
        response = self.c.post('http://127.0.0.1:8000/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)

'''
此 用 例 要 想 运 行 通 过 ， 需 要 在 views.py 视 图 文 件 中 将 event_manage() 和 search_name() 函 数 的
@login_required 装饰器去掉， 因为这两个函数依赖于登录， 然而， Client()所提供的 get()和 post()方法并没有验证登录的参数
'''
#发布会管理
class EventManageTest(TestCase):
    ''' 发布会管理 '''
    def setUp(self):
        Event.objects.create(id=2, name='xiaomi5', limit=2000, status=True, address='beijing', start_time=datetime(2016, 8, 10, 14, 0, 0))
        self.c = Client()
    def test_event_manage_success(self):
        ''' 测试发布会:xiaomi5 '''
        response = self.c.post('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"xiaomi5", response.content)
        self.assertIn(b"beijing", response.content)
    def test_event_manage_search_success(self):
        ''' 测试发布会搜索 '''
        response = self.c.post('/search_name/', {"name": "xiaomi5"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"xiaomi5", response.content)
        self.assertIn(b"beijing", response.content)

#嘉宾管理
class GuestManageTest(TestCase):
    ''' 嘉宾管理 '''
    def setUp(self):
        Event.objects.create(id=1, name="xiaomi5", limit=2000, address='beijing', status=1, start_time=datetime(2016,8,10,14,0,0))
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0, event=1)
        self.c = Client()
    def test_event_manage_success(self):
        ''' 测试嘉宾信息: alen '''
        response = self.c.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"alen", response.content)
        self.assertIn(b"18611001100", response.content)
    def test_guest_manage_search_success(self):
        ''' 测试嘉宾搜索 '''
        response = self.c.post('/guest_search_name/', {"phone": "18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"alen", response.content)
        self.assertIn(b"18611001100", response.content)

'''
首先用例要想运行通过， 需要在 views.py 视图文件中将 sign_index_action()函数的@login_required 装饰器去掉， 原因同上。
其次， 关于签到功能， 测试的情况比较多， 所以在 setUp()中创建测试数据需要注意。 创建了两条发布会
“xiaomi5” 和“oneplus4” ， 嘉宾“alen” 所属于“xiaomi5” ， 嘉宾“una” 所属于“oneplus4” ， 并且“una”的签到状态为已签到。
当通过“alen”的手机号（18611001100）在“oneplus4”发布会页面签到时会， 将会提示：“event id or phoneerror.” 
发布会 id 与手机号不匹配。当通过“una” 手机号签到时， 将会提示： “user has sign in.” 用户已签到。
'''
#发布会签到
class SignIndexActionTest(TestCase):
    ''' 发布会签到 '''
    def setUp(self):
        Event.objects.create(id=1, name="xiaomi5", limit=2000, address='beijing', status=1, start_time='2017-8-10 12:30:00')
        Event.objects.create(id=2, name="oneplus4", limit=2000, address='shenzhen', status=1, start_time='2017-6-10 12:30:00')
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0, event=1)
        Guest.objects.create(realname="una", phone=18611001101, email='una@mail.com', sign=1, event=2)
        self.c = Client()
    def test_sign_index_action_phone_null(self):
        ''' 手机号为空 '''
        response = self.c.post('/sign_index_action/1/', {"phone": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"phone error.", response.content)
    '''def test_sign_index_action_phone_or_event_id_error(self):
         手机号或发布会 id 错误 
        response = self.c.post('/sign_index_action/2/',{"phone":"18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"event id or phone error.", response.content)'''
    def test_sign_index_action_user_sign_has(self):
        ''' 用户已签到 '''
        response = self.c.post('/sign_index_action/2/', {"phone": "18611001101"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"user has sign in.", response.content)
    def test_sign_index_action_sign_success(self):
        ''' 签到成功 '''
        response = self.c.post('/sign_index_action/1/', {"phone": "18611001100"})
        self.assertEqual(response.status_code, 200)


