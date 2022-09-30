from . import db


class Eventlist(db.Model):
    __tablename__ = 'eventlist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String(255))
    ip = db.Column(db.String(255))
    level = db.Column(db.String(255))
    status = db.Column(db.String(255))
    msg = db.Column(db.Text)
    startAt = db.Column(db.DateTime)
    endAt = db.Column(db.DateTime)
    perAt = db.Column(db.Time)
    alertname = db.Column(db.String(255))
    eventid = db.Column(db.Integer)


