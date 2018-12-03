
import hashlib

'''
鉴权： 通过客户的密钥， 服务端的密钥匹配；这个很有好理解， 例如一个接口传参为：
http://127.0.0.1:8000/api/?a=1&b=2
假设签名的密钥为： @admin123
加上签名之后的接口参数为：
http://127.0.0.1:8000/sign/?a=1&b=2&sign=@admin123
显然， sign 参数明文传输是不安全的， 所以， 一般会通过加密算法进行加密。
'''
#MD5加密
md5 = hashlib.md5()
sign_str = "@admin123"
sign_bytes_utf8 = sign_str.encode(encoding="utf-8")
md5.update(sign_bytes_utf8)
sign_md5 = md5.hexdigest()
print(sign_md5)