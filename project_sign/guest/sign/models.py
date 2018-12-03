
from django.db import models
# Create your models here.

'''
首先， 发布会表和嘉宾表中默认都会生成自增 id， 而我们在创建模型时不需要声明该字段。
其次， 发布会表中增加了 status 字段用于表示发布会的状态是否开启， 用于控制该发布会是否可用。
再次， 嘉宾表中通过 event_id 关联发布会表， 一条嘉宾信息一定所属于某一场发布会。
最后， 对于一场发布会来说， 一般会选择手机号作为一位嘉宾的验证信息， 所以， 对于一场发布会来说，
手机号必须是唯一。 除了嘉宾 id 外， 这里通过发布会 id +手机号来做为联合主键。
__str__()方法告诉 Python 如何将对象以 str 的方式显示出来。 所以， 为每个模型类添加了__str__()方法。
（如果读者使用的是 Python2.x 的话， 这里需要使用__unicode__()） 。
'''

# 发布会表
class Event(models.Model):

    name = models.CharField(max_length=100)                     # 发布会标题
    limit = models.IntegerField()                               # 参加人数
    status = models.BooleanField()                              # 状态
    address = models.CharField(max_length=200)                  # 地址
    start_time = models.DateTimeField('events time')            # 发布会时间
    create_time = models.DateTimeField(auto_now=True)           # 创建时间（自动获取当前时间）

    def __str__(self):
        return self.name

# 嘉宾表
class Guest(models.Model):

    event = models.IntegerField(Event)                          # 关联发布会 id
    realname = models.CharField(max_length=64)                  # 姓名
    phone = models.CharField(max_length=16)                     # 手机号
    email = models.EmailField()                                 # 邮箱
    sign = models.BooleanField()                                # 签到状态
    create_time = models.DateTimeField(auto_now=True)           # 创建时间（自动获取当前时间）

    class Meta:
        unique_together = ("event", "phone")

    def __str__(self):
        return self.realname