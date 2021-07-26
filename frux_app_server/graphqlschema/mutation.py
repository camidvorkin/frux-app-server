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
from .objects.stage import (
    ProjectStageMutation,
    RemoveProjectStageMutation,
    UpdateProjectStageMutation,
)
from .objects.user import (
    BlockUserMutation,
    RemoveSeerMutation,
    SetSeerMutation,
    UnBlockUserMutation,
    UpdateUser,
    UserMutation,
)


class Mutation(graphene.ObjectType):
    class Meta:
        description = 'Create/Update/Delete something in the database such as creating users, updating information about details in a project, etc.'

    mutate_user = UserMutation.Field(
        description='Creates a new user in Frux. User\'s email must be unique to be able to register it correctly'
    )
    mutate_project = ProjectMutation.Field(
        description='Create a new project in Frux. Very basic information, such as name or description, is needed to create the project.'
    )
    mutate_admin = AdminMutation.Field(
        description='Creates a new admin with a token. Use for server testing.'
    )
    mutate_update_user = UpdateUser.Field(
        description='Allows a User to update their own infomation about them in their profile.'
    )
    mutate_set_seer = SetSeerMutation.Field(
        description='Set as seer to those users who request to have that role.'
    )
    mutate_remove_seer = RemoveSeerMutation.Field(
        description='Remove the role of supervising from those users who ask not to have this responsibility anymore.'
    )
    mutate_block_user = BlockUserMutation.Field(description='Block user from system.')
    mutate_unblock_user = UnBlockUserMutation.Field(
        description='Unblock user from system.'
    )
    mutate_update_project = UpdateProject.Field(
        description='Allows the owner of the project to update their project\'s infomation.'
    )
    mutate_invest_project = InvestProject.Field(
        description='The action of a user investing in a certain project an amount `invested_amount` of money.'
    )
    mutate_seer_project = SeerProjectMutation.Field(
        description='Once the project\'s stages and information are ready and you want to start the project, the state of the project is changed and a seer is assigned.'
    )
    mutate_block_project = BlockProjectMutation.Field(
        description='Block project from system.'
    )
    mutate_unblock_project = UnBlockProjectMutation.Field(
        description='Unblock project from system.'
    )
    mutate_fav_project = FavProject.Field(
        description='Add a favourite to a specific project.'
    )
    mutate_unfav_project = UnFavProject.Field(
        description='Remove a favourite to a specific project.'
    )
    mutate_project_stage = ProjectStageMutation.Field(
        description='Creates a new project stage.'
    )
    mutate_withdraw_funds = WithdrawFundsMutation.Field(
        description='Sponsor withdraws the funds sent to a project. Withdraw `withdraw_amount` or the entire investment.'
    )
    mutate_review_project = ReviewProjectMutation.Field(
        description='Give the project a quantitative and qualitative review.'
    )
    mutate_complete_stage = CompleteStageMutation.Field(
        description='Sets a stage(and all of the previous) as completed if the project is IN PROGRESS.'
    )
    mutate_cancel_project = CancelProjectMutation.Field(
        description='Cancel the project'
    )
    mutate_update_project_stage = UpdateProjectStageMutation.Field()
    mutate_remove_project_stage = RemoveProjectStageMutation.Field()
