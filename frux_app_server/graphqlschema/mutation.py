import graphene

from .objects.admin import AdminMutation
from .objects.favorite import FavProject, UnFavProject
from .objects.investment import InvestProject, WithdrawFundsMutation
from .objects.project import (
    BlockProjectMutation,
    CancelProjectMutation,
    CompleteStageMutation,
    ProjectMutation,
    SeerProjectMutation,
    UnBlockProjectMutation,
    UpdateProject,
)
from .objects.review import ReviewProjectMutation
from .objects.stage import ProjectStageMutation
from .objects.user import (
    BlockUserMutation,
    RemoveSeerMutation,
    SetSeerMutation,
    UnBlockUserMutation,
    UpdateUser,
    UserMutation,
)


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()
    mutate_admin = AdminMutation.Field()
    mutate_update_user = UpdateUser.Field()
    mutate_set_seer = SetSeerMutation.Field()
    mutate_remove_seer = RemoveSeerMutation.Field()
    mutate_block_user = BlockUserMutation.Field()
    mutate_unblock_user = UnBlockUserMutation.Field()
    mutate_update_project = UpdateProject.Field()
    mutate_invest_project = InvestProject.Field()
    mutate_seer_project = SeerProjectMutation.Field()
    mutate_block_project = BlockProjectMutation.Field()
    mutate_unblock_project = UnBlockProjectMutation.Field()
    mutate_fav_project = FavProject.Field()
    mutate_unfav_project = UnFavProject.Field()
    mutate_project_stage = ProjectStageMutation.Field()
    mutate_withdraw_funds = WithdrawFundsMutation.Field()
    mutate_review_project = ReviewProjectMutation.Field()
    mutate_complete_stage = CompleteStageMutation.Field()
    mutate_cancel_project = CancelProjectMutation.Field()
