import graphene
import sqlalchemy

from frux_app_server.graphqlschema.object import Favorites
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.models import Favorites as FavoritesModel
from frux_app_server.models import db
from frux_app_server.services.chat_client import chat_client


class FavProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Favorites

    @requires_auth
    def mutate(self, info, id_project):

        fav = FavoritesModel(user_id=info.context.user.id, project_id=id_project,)

        try:
            db.session.add(fav)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            pass

        chat_client.subscribe_project_watcher(id_project, info.context.user.id)
        return fav


class UnFavProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Favorites

    @requires_auth
    def mutate(self, info, id_project):

        FavoritesModel.query.filter_by(
            user_id=info.context.user.id, project_id=id_project
        ).delete()
        db.session.commit()

        chat_client.unsubscribe_project_watcher(id_project, info.context.user.id)
        return FavoritesModel(user_id=info.context.user.id, project_id=id_project,)
