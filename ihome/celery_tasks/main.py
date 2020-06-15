from celery import Celery


# 利用导入的 Celery 创建对象
celery_app = Celery('lovehome')

# 创建的 config 配置文件:
celery_app.config_from_object('celery_tasks.config')

# 让 celery_app 自动捕获目标地址下的任务:
# 就是自动捕获 tasks, 自动注册 celery 任务
celery_app.autodiscover_tasks(['celery_tasks.msm'])