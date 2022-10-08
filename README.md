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
git clone https://github.com/mrzhxl/alert_notice.git
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

## 接口描述
**接收告警信息并发送给飞书机器人**

```bash
接口URL：POST http://{IP}:{PORT}/AlertFeishu
```
### 输入参数
**prometheus alertmanage发送的数据，及自定义项**
|参数名称|必选|类型|描述|
|----|---|---|---|
|alerts|是|Object|告警信息列表|
|alerts.status|是|String|告警状态，alertmanager传入[firing or resolved]
|alerts.labels|是|Object|prometheus的label项|
|alerts.labels.alertname|是|String|事件名称|
|alerts.labels.hostname|是|String|告警主机名|
|alerts.labels.instance|是|String|告警主机IP地址|
|alerts.labels.job|否|String|prometheus的job名称|
|alerts.labels.severity|是|String|告警等级|
|alerts.annotations|是|Object|告警信息备注|
|alerts.annotations.description|是|String|告警内容描述|
|alerts.annotations.project|否|String|告警项目名|
|alerts.annotations.value|是|String|告警的取值|
|alerts.startsAt|是|datetime|告警开始时间|
|alerts.endsAt|是|datetime|告警结束时间|


**输入示例（python3）**
```python3
import requests

url = "http://127.0.0.1:8888/AlertFeishu"

payload = {
    "receiver": "xxx",
    "status": "firing",
    "alerts": [
        {
            "status": "xxx",               
            "labels": {                     
                "alertname": "xxx",         
                "hostname": "xxx",          
                "instance": "xxx",          
                "job": "xxx",
                "severity": "xxx"           
            },
            "annotations": {
                "description": "xxx",
                "project": "xxx",
                "value": "xxx"              
            },
            "startsAt": "1970-01-01T01:10:10.001Z",
            "endsAt": "1970-01-01T01:10:20.001Z",
            ...
        }，
        {
            "status": "",
            "labels": {
                ...
            },
            ...
        }
    ],
    ...
}
response = requests.request("POST", url, json=payload)

print(response.text)
```
**输出示例**
```python3
# 成功
{
    "code": 200,
    "message": "success"
}

# 失败（请检查传入参数）
{
    "code": 403,
    "message": "The data type is wrong"
}
```
**告警记录列表**
```bash
接口URL: GET http://{IP}:{PORT}/showalert
# 告警记录,查询数据库中记录对事件id（eventid字段去重），告警开始时间降序显示，默认前100条
```
**确认事件（类似zabbix知悉功能）**
```bash
接口URL: GET http://{IP}:{PORT}/ack/{eventid}
# 告警知悉，相同事件id不会在记录和发送给飞书机器人
# {eventid} 从/showalert接口中查找
```
**输入参数**
|参数名称|必选|类型|描述|
|----|---|---|---|
|eventid|是|int|事件id，在/showalert接口中查找|
## 程序启动
```bash
# uwsgi启动
uwsgi --ini alert_start.ini
# 或直接运行manage.py
python3 manage.py
# 程序端口 8000
```