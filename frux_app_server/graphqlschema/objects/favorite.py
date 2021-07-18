import graphene
import sqlalchemy

from frux_app_server.graphqlschema.object import Favorites
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.models import Favorites as FavoritesModel
from frux_app_server.models import db


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
        return FavoritesModel(user_id=info.context.user.id, project_id=id_project,)
