from django.contrib import admin
from sign.models import Event, Guest
# Register your models here.

'''
新建了 EventAdmin 类， 继承 django.contrib.admin.ModelAdmin 类， 
保存着一个类的自定义配置， 以供Admin 管理工具使用。 
这里只自定义了一项： list_display， 它是一个字段名称的数组， 用于定义要在列表中显示哪些字段。 
当然， 这些字段名称必须是模型中的 Event()类定义的。
接下来修改 admin.site.register()调用， 添加了 EventAdmin。 你可以这样理解： 用 EventAdmin 选项注册Event 模块。
然后， 对 Guest 模块也做了同样的操作。
除此之外， Admin 管理后台提供了的很强的定制性， 我们甚至可以非常方便生成搜索栏和过滤器。
search_fields 用于创建表字段的搜索器， 可以设置搜索关键字匹配多个表字段。 list_filter 用于创建字段过滤器。
'''

class EventAdmin(admin.ModelAdmin):

    list_display = ['name', 'status', 'start_time', 'id']
    search_fields = ['name']  # 搜索栏
    list_filter = ['status']  # 过滤器

class GuestAdmin(admin.ModelAdmin):

    list_display = ['realname', 'phone', 'email', 'sign', 'create_time', 'event']
    search_fields = ['realname', 'phone']  # 搜索栏
    list_filter = ['sign']  # 过滤器

admin.site.register(Event,EventAdmin)

admin.site.register(Guest,GuestAdmin)