from ..models import Eventlist
from .. import db

class alertRule:
    def firing_rule(self,current_alertname,current_eventid):
        if current_alertname == '交换机带宽超过100M':
            """
            记录中匹配'网关公网带宽超过150M'，状态是告警，返回True
            """
            eventlist = Eventlist.query.filter(Eventlist.alertname == '网关公网带宽超过150M').filter(Eventlist.status == '告警').first()
            if eventlist:
                return True
            else:
                return False
        else:
            """
            状态是知悉，事件id匹配。返回False
            """
            eventlist = Eventlist.query.filter(Eventlist.status == '知悉').filter(Eventlist.eventid == current_eventid).first()
            if eventlist:
                return False
            else:
                return True

    def resolved_rule(self, current_alertname, current_eventid):
        eventid = Eventlist.query.filter(Eventlist.status != '恢复').filter(Eventlist.alertname == current_alertname).filter(Eventlist.eventid == current_eventid).first()
        if eventid:
            return True
        else:
            return False
