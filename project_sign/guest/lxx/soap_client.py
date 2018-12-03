
from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import

# 使用库 suds_jurko： https://bitbucket.org/jurko/suds
# web service 查询： http://www.webxml.com.cn/zh_cn/web_services.aspx
# 电话号码归属地查询
url = 'http://ws.webxml.com.cn/WebServices/MobileCodeWS.asmx?wsdl'
client = Client(url)
result = client.service.getMobileCodeInfo(18939827819)
print(result)

url = 'http://ws.webxml.com.cn/WebServices/WeatherWS.asmx?wsdl'
imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
imp.filter.add('http://WebXml.com.cn/')
client = Client(url, plugins=[ImportDoctor(imp)])
result = client.service.getWeatherbyCityName("北京")
print(result)