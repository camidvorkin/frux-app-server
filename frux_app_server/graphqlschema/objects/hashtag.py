from frux_app_server.models import (
    AssociationHashtag as AssociationHashtagModel,  # pylint: disable=unused-import
)
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import db


def add_hashtags(hashtags, project_id):
    for h in hashtags:
        if db.session.query(HashtagModel).filter_by(hashtag=h).count() != 1:
            hashtag = HashtagModel(hashtag=h)
            db.session.add(hashtag)

        association = AssociationHashtagModel(hashtag=h, project_id=project_id)
        db.session.add(association)
    db.session.commit()


def delete_hashtags(project_id):
    db.session.query(AssociationHashtagModel).filter_by(project_id=project_id).delete()
