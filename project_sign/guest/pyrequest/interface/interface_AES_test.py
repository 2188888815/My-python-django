from Crypto.Cipher import AES
import base64
import requests
import unittest
import json

'''
self.app_key = 'W7v4D60fds2Cmk2U'  payload = {'eid': '1', 'phone': '13800138000'}
首先， 定义好 app_key 和接口参数， app_key 是密钥， 只有合法的调用者才知道， 这个一定要保密噢！ 这
里同样选择使用字典格式来存放接口参数。
encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
首先将 payload 参数转化为 json 格式， 然后将参数和 app_key 传参给 encryptAES()方法用于生成加密串。
def encryptAES(self,src, key):
"""生成 AES 密文"""
iv = b"1172311105789011"
cryptor = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cryptor.encrypt(self.pad(src))
return self.encryptBase64(ciphertext)
IV 同样是保密的， 并且我们前面知道它必须是 16 位字节。 然后通过 encrypt()方法对 src 接口参数生成
加密串， 但是这里会有问题。 encrypt()要加密的字符串有严格的长度要求， 长度必须是 16 的倍数。 如果直接生成可能会提示：
ValueError: Input strings must be a multiple of 16 in length
可是， 被加密字符串的长度是不可控。 接口参数的个数和长度可能会随意的变化。 所以， 为了解决这个
问题， 还需要对参数字符串时行处理， 使其长度固定。
self.pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
这是函数式编程的一种用法， 通过 lambda 定义匿名函数来对字符串进行补足， 使其长度为 16 的倍数。
再接下来生成的字符串是这样的：
b'>_\x80\x1fi\x97\x8f\x94~\xeaE\xectBm\x9d\xa9\xc5\x85<+e\xa5lW\xe1\x84}\xfa\x8b\xb9\xde\x1a\x10J\xcd\xc5\xa1A4Z\xff\x05x\xe3\xf1\x00Z'
但这样的字符串太长， 并不太适合传输。
def encryptBase64(self,src):
return base64.urlsafe_b64encode(src)
通过 base64 模块的 urlsafe_b64encode()方法对 AES 加密串进行二次加密。
然后得到的字符串是这样的：
b'gouBbuKWEeY5wWjMx-nNAYDTion0ADOysaLw1uzzGOpvTTASpQGJu5p0WuDhZMiM' 到此， 加密过程结束。
r = requests.post(self.base_url, data={"data": encoded})
将加密后的字符串作为接口的 data 参数发送给接口。
当服务器接收到字符串之后， 如何对加密串进行解密处理呢？ 下接来开发服务器端的处理。
'''

class AESTest(unittest.TestCase):
    def setUp(self):
        BS = 16
        self.pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        self.base_url = "http://127.0.0.1:8000/sign/sec_get_guest_list/"
        self.app_key = 'W7v4D60fds2Cmk2U'

    def encryptBase64(self,src):
        return base64.urlsafe_b64encode(src)

    def encryptAES(self,src, key):
        """生成 AES 密文"""
        iv = b"1172311105789011"
        cryptor = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cryptor.encrypt(self.pad(src))
        return self.encryptBase64(ciphertext)

    def test_aes_interface(self):
        '''test aes interface'''
        payload = {'eid': '1', 'phone': '13800138000'}
        # 加密
        encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
        r = requests.post(self.base_url, data={"data": encoded})
        result = r.json()
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], "success")

    def test_get_guest_list_eid_null(self):
        ''' eid 参数为空 '''
        payload = {'eid': '','phone': ''}
        encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
        r = requests.post(self.base_url, data={"data": encoded})
        result = r.json()
        self.assertEqual(result['status'], 10021)
        self.assertEqual(result['message'], 'eid cannot be empty')

    def test_get_event_list_eid_error(self):
        ''' 根据 eid 查询结果为空 '''
        payload = {'eid': '901','phone': ''}
        encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
        r = requests.post(self.base_url, data={"data": encoded})
        result = r.json()
        self.assertEqual(result['status'], 10022)
        self.assertEqual(result['message'], 'query result is empty')

    def test_get_event_list_eid_success(self):
        ''' 根据 eid 查询结果成功 '''
        payload = {'eid': '1','phone': ''}
        encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
        r = requests.post(self.base_url, data={"data": encoded})
        result = r.json()
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], 'success')
        self.assertEqual(result['data'][0]['realname'],'张三')
        self.assertEqual(result['data'][0]['phone'],'13800138000')

    def test_get_event_list_eid_phone_null(self):
        ''' 根据 eid 和 phone 查询结果为空 '''
        payload = {'eid':2,'phone':'10000000000'}
        encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
        r = requests.post(self.base_url, data={"data": encoded})
        result = r.json()
        self.assertEqual(result['status'], 10022)
        self.assertEqual(result['message'], 'query result is empty')

    def test_get_event_list_eid_phone_success(self):
        ''' 根据 eid 和 phone 查询结果成功 '''
        payload = {'eid':1,'phone':'18633003301'}
        encoded = self.encryptAES(json.dumps(payload), self.app_key).decode()
        r = requests.post(self.base_url, data={"data": encoded})
        result = r.json()
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['message'], 'success')
        self.assertEqual(result['data']['realname'],'alen')
        self.assertEqual(result['data']['phone'],'18633003301')