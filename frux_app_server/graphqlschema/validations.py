import re

from frux_app_server.models import Category as CategoryModel
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import db


def is_email_valid(email):
    return re.match(
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
        email,
    )


def is_location_valid(latitude, longitude):
    return re.match(r"^(\-?([0-8]?[0-9](\.\d+)?|90(.[0]+)?))$", latitude) and re.match(
        r"^(\-?([1]?[0-7]?[0-9](\.\d+)?|180((.[0]+)?)))$", longitude
    )


def is_category_invalid(category):
    return (
        category
        and db.session.query(CategoryModel).filter_by(name=category).count() != 1
    )


def has_already_invest(id_project, id_user):
    return (
        db.session.query(InvestmentsModel)
        .filter_by(project_id=id_project, user_id=id_user)
        .count()
        >= 1
    )


def has_seer():
    return db.session.query(UserModel).filter_by(is_seer=True).count() > 0
