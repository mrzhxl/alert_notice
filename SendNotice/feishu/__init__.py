from flask import Blueprint
feishu = Blueprint('feishu', __name__)

from . import views
from . import rules