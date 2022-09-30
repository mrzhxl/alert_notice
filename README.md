# 告警通知
prometheus告警发送给飞书机器人

## 环境
```bash
mysql5.7+
python3.9+
Flask 2.2.2+
Flask-SQLAlchemy 2.5.1+
```
## 目录介绍
```bash
alert_notice
    SendNotice
        __init__ -> 创建函数create_app(初始化flask,sqlalche、注册蓝图register_blueprint(feishu))
        feishu
            __init__ -> 创建蓝图、导入视图文件
            views -> （route get、post)、utc时间转换cst、持续时间、发送给飞书机器人
            rules -> 告警和恢复规则
        models
            数据库
        templates
            告警模版文件、恢复告警模版文件
    manage -> load func crate_app run (init db)
```
## 使用方法
```bash
git clone 
cd alert_notice
# 安装依赖包
pip3 install -r requirements.txt

# 更改数据库地址和飞书机器人地址配置
vim config.py   # 配置中分为测试环境和正式环境，根据自己需求来更改
class Config(object) # 正式环境配置
class TestConfig(Config) # 测试环境配置
# 注意： 创建数据库和账号授权自行处理

vim alert_notice/SendNotice/__init__.py
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.TestConfig') # 更改使用配置
    db.init_app(app)

    from .feishu import feishu
    app.register_blueprint(feishu)
    return app
```

## 接口说明
### POST /AlertFeishu
```bash
# 接收告警信息并发送给飞书机器人


# prometheus alertmanage发送的数据，如labels的值不一致请自行更改
{
    ...
    "status": "firing",
    "alerts": [
        {
            "status": "",
            "labels": {
                "alertname": "",
                "hostname": "",
                "instance": "",
                "job": "",
                "severity": ""
            },
            "annotations": {
                "description": "",
                "project": "",
                "value": ""
            },
            "startsAt": "",
            "endsAt": "",
            ...
        }
    ],
    ...
}

## 程序获取的值，不一致自行更改
AlertName = data.get('alerts')[0].get('labels').get('alertname')
Hostname = data.get('alerts')[0].get('labels').get('hostname')
Ip = data.get('alerts')[0].get('labels').get('instance')
Value = data.get('alerts')[0].get('annotations').get('value')
Level = data.get('alerts')[0].get('labels').get('severity')
Msg = data.get('alerts')[0].get('annotations').get('description')
StartsAt = utc_to_cst(data.get('alerts')[0].get('startsAt'))
EndAt = utc_to_cst(data.get('alerts')[0].get('endsAt'))
```
### GET /showalert
```bash
# 告警记录
# 不会写前端，只做个列表
```
### GET /ack/eventid
```bash
# 告警知悉，相同事件id不会在记录和发送给飞书机器人
# eventid 从/showalert查找
```
## 程序启动
```bash
# uwsgi启动
uwsgi --ini alert_start.ini
# 或直接运行manage.py
python3 manage.py
# 程序端口 8000
```