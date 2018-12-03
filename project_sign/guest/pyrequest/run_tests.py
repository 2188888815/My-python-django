import time, sys
sys.path.append('./interface')
sys.path.append('./db_fixture')
from pyrequest.HTMLTestRunner import HTMLTestRunner
from unittest import defaultTestLoader
from pyrequest.db_fixture import test_data

'''
首先， 通过调用 test_data.py 文件中的 init_data()函数来初始化接口测试数据。
使用 unittest 框架所提供的 discover()方法， 查找 interface/ 目录下， 所有匹配*_test.py 的测试文件（*星号匹配任意字符）。
HTMLTestRunner 为 unittest 单元测试框架的扩展，利用它所提供的 HTMLTestRunner()类来替换 unittest单元测试框架的 TextTestRunner()类，
从而生成 HTML 格式的测试报告。
遗憾的是 HTMLTestRunner 并不支持 Python3.x， 我对其做了少量的修改， 其它可以在 Python3 下执行。
通过 time 的 strftime()方法获取当前时间， 并且转化成一定的时间格式。 作为测试报告的名称。 
这样做目的是是为了避免因为生成的报告的名称重名而造成报告的覆盖。 最终， 将测试报告存放于 report/目录下面生成完整的接口自动化测试报告。
'''
# 指定测试用例为当前文件夹下的 interface 目录
test_dir = './interface'
testsuit = defaultTestLoader.discover(test_dir, pattern='*_test.py')


if __name__ == "__main__":
    test_data.init_data() # 初始化接口测试数据

    now = time.strftime("%Y-%m-%d %H_%M_%S")
    filename = './report/' + now + '_result.html'
    fp = open(filename, 'wb')
    runner = HTMLTestRunner(stream=fp,
                            title='发布会签到系统接口自动化测试',
                            description='运行环境：MySQL(PyMySQL), Requests, unittest ')
    runner.run(testsuit)
    fp.close()
