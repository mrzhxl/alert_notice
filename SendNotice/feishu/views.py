#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, redirect, url_for, jsonify,current_app
from datetime import datetime, timedelta
from ..models import Eventlist
from .. import db
from . import feishu
from .rules import alertRule
import hashlib
import requests
import json



rule = alertRule()


def send_feishu(url, msg):

    headers = {'Content-Type': 'application/json'}

    body = {
        "msg_type": "text",
        "content": {
            "text": msg
        }
    }

    req = requests.post(url, headers=headers, data=json.dumps(body))
    return req.status_code

# 时间转换
def utc_to_cst(utc_time, utc_format="%Y-%m-%dT%H:%M:%S.%fZ", cst_format="%Y-%m-%d %H:%M:%S"):
    timestamp = datetime.strptime(utc_time, utc_format)
    cststamp = timestamp + timedelta(hours=8)
    return datetime.strftime(cststamp, cst_format)

# 持续时间计算
def time_cal(starttime, endtime):
    time_format = "%Y-%m-%d %H:%M:%S"
    startstamp = datetime.strptime(starttime, time_format)
    endstamp = datetime.strptime(endtime, time_format)
    persistenstamp = endstamp - startstamp
    return persistenstamp


@feishu.route("/showalert")
def get_alarm_history():
    if request.method == 'GET':
        num = request.args.get('num',100)
        # 根据eventid去重
        datalist = Eventlist.query.with_entities(Eventlist.eventid,Eventlist.alertname,Eventlist.hostname,Eventlist.ip,Eventlist.level,Eventlist.msg,Eventlist.startAt,Eventlist.endAt,Eventlist.perAt,Eventlist.status).distinct(Eventlist.eventid).order_by(Eventlist.startAt.desc()).limit(num).all()
        linedata = []
        for dataline in datalist:
            data = dict(dataline)
            data['startAt'] = str(data['startAt'])
            data['endAt'] = str(data['endAt'])
            data['perAt'] = str(data['perAt'])
            linedata.append(data)
        # return jsonify(linedata)
        return render_template('alarmhistory.html', datalist=linedata)

# 知悉
@feishu.route('/ack/<eventid>')
def event_confirm(eventid):
    for eventlist in Eventlist.query.filter(Eventlist.eventid == eventid).filter(Eventlist.status == '告警').all():
        # 更新告警记录
        eventlist.status = '知悉'
        db.session.commit()
    return redirect(url_for('feishu.get_alarm_history'))

@feishu.post("/AlertFeishu")
def alert_feishu():
    try:
        data = request.get_json()
        print(data)
        for alert in data.get('alerts'):
            AlertName = alert.get('labels').get('alertname')
            Hostname = alert.get('labels').get('hostname')
            Ip = alert.get('labels').get('instance')
            Value = alert.get('annotations').get('value')
            Level = alert.get('labels').get('severity')
            Msg = alert.get('annotations').get('description')

            # start时间转换
            # 判断报警、恢复状态发送不同模版
            # 报警
            if alert.get('status') == 'firing':
                StartsAt = utc_to_cst(alert.get('startsAt'))
                # 生成事件id
                Eventid = int(str(int(hashlib.md5((AlertName+Hostname+Ip+StartsAt).encode('utf-8')).hexdigest(),16))[-6:])
                # 匹配策略规则是否通过
                rule_pass = rule.firing_rule(AlertName,Eventid)
                if rule_pass:
                    # 写入数据库
                    eventlist = Eventlist(
                        hostname=Hostname,
                        ip=Ip,
                        level=Level,
                        status='告警',
                        msg=Msg,
                        startAt=StartsAt,
                        alertname=AlertName,
                        eventid=Eventid
                    )
                    db.session.add(eventlist)
                    db.session.commit()
                    firing_value = render_template('firing.html', **locals())
                    # 飞书告警
                    req = send_feishu(current_app.config.get('FEISHU_BOT'), firing_value)
                    if req == 200:
                        print('send feishu ok')
                    else:
                        print('send feishu fail')
                else:
                    print('no alarm')

            # 恢复
            elif alert.get('status') == 'resolved':
                StartsAt = utc_to_cst(alert.get('startsAt'))
                EndAt = utc_to_cst(alert.get('endsAt'))
                PersistentAt = time_cal(utc_to_cst(alert.get(
                    'startsAt')), utc_to_cst(alert.get('endsAt')))
                # 生成事件id
                Eventid = int(str(int(hashlib.md5((AlertName+Hostname+Ip+StartsAt).encode('utf-8')).hexdigest(),16))[-6:])

                rule_pass = rule.resolved_rule(AlertName, Eventid)
                if rule_pass:
                    # 查询数据库中告警记录
                    for eventlist in Eventlist.query.filter(Eventlist.eventid == Eventid).all():
                        # 更新告警记录
                        eventlist.status = '恢复'
                        eventlist.endAt = EndAt
                        eventlist.perAt = PersistentAt
                        db.session.commit()
                    resolved_value = render_template('resolved.html', **locals())
                    # 飞书告警
                    req = send_feishu(current_app.config.get('FEISHU_BOT'), resolved_value)
                    if req == 200:
                        print('send feishu ok')
                    else:
                        print('send feishu fail')
                else:
                    print('no data')
        return jsonify({"code": 200, "message": "success"})
    except Exception as e:
        print(e)
        return jsonify({"code": 403, "message": "The data type is wrong"})