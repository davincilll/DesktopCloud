from django.db import models


# Create your models here.

# 这里写自己的user
# 然后自己写认证类

class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)
    # 书签配置
    bookmarkConfig = models.JSONField(default={})
    # 导航配置
    navigationConfig = models.JSONField(default={})
    # 这里使用邮箱注册方式去实现

    def __str__(self):
        return self.email
