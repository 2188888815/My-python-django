import unittest
from lxx.count import Claculator

'''
首先， 通过 import 导入 unittest 单元测试框架。
创建 CountTest 类继承 unittest.TestCase 类。
setUp()和 tearDown()在单元测试框架中比较特别， 它们分别在每一个测试用例的开始和结束执行。setUp()
方法用于测试用例执行前的初始化工作， 例如初始化变量、 生成数据库测试数据、 打开浏览器等。 tearDown()
方法与 setUp()方法相呼应， 用于测试用例执行之后的善后工作， 例如清除数据库测试数据、 关闭文件、 关闭浏览器等。
unittest 要求测试方法必须以“test” 开头。 例如， test_add、 test_sub 等。
接下来， 调用 unittest.TestSuite()类中的 addTest()方法向测试套件中添加测试用例。 简单的可以将测试套件理解成运行测试用例的集合。
通过 unittest.TextTestRunner()类中的 run()方法运行测试套件中的测试用例。
如果想默认运行当前测试文件下的所有测试用例， 可以直接使用 unittest.main()方法。 那么 main()方法在查找测试用例时按照两个规则。
首先， 该测试类必须继承 unittest.TestCase 类； 其次， 该测试类下面的方法必须以“test” 开头。
'''
#单元测试例，计算器
class CountTest(unittest.TestCase):

    def setUp(self):
        self.cal = Claculator(8, 4)

    def tearDown(self):
        pass

    def test_add(self):
        result = self.cal.add()
        self.assertEqual(result, 12)

    def test_sub(self):
        result = self.cal.sub()
        self.assertEqual(result, 4)

    def test_mul(self):
        result = self.cal.mul()
        self.assertEqual(result, 32)

    def test_div(self):
        result = self.cal.div()
        self.assertEqual(result, 2)

if __name__ == "__main__":

    #unittest.main()
    # 构造测试集
    suite = unittest.TestSuite()
    suite.addTest(CountTest("test_add"))
    suite.addTest(CountTest("test_sub"))
    suite.addTest(CountTest("test_mul"))
    suite.addTest(CountTest("test_div"))
    # 执行测试
    runner = unittest.TextTestRunner()
    runner.run(suite)