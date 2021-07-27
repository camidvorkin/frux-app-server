import os

import requests


class ChatException(Exception):
    pass


# ProjectCreator
#   - Quien se suscribe? el creador de un proyecto al crearlo
#   - Que notificaciones recibe? NewSeederNotification, NewStageNotification_creator, NewSeer_creator, ChangeStateNotification,
# ProjectWatcher
#   - Quien se suscribe? los que dieron like
#   - Que notificaciones recibe? ChangeStateNotification,
# ProjectSeer
#   - Quien se suscribe? el veedor de un proyecto
#   - Que notificaciones recibe? NewSeederNotification, NewSeer_seer, ChangeStateNotification, FinishStageNotification_seeder,
# ProjectSeeder
#   - Quien se suscribe? los que invirtieron en el proyecto
#   - Que notificaciones recibe? NewStageNotification_noncreator, FinishStageNotification_noncreator,
# El chat NO se maneja por suscripciones


class ChatClient:
    def __init__(self):
        self.url = os.environ.get('FRUX_CHAT_URL', 'http://localhost:5500')

    def _request(
        self,
        path,
        expected_code=None,
        message='make request',
        func=requests.get,
        body=None,
    ):
        if not body:
            body = {}
        try:
            r = func(f'{self.url}{path}', json=body)
        except requests.ConnectionError:
            # TODO: log this
            return
            # raise ChatException(
            #    f'Unable to {message}! Notification service is down!'
            # ) from e
        if expected_code and r.status_code != expected_code:
            return ChatException(f'Unable to {message}! {r.status_code} - {r.text}')

        res = {}
        res['_status_code'] = r.status_code
        res['_text'] = r.text

        return res

    def _subscription_request(self, project_id, user_id, role, func=requests.post):
        return self._request(
            f'/subscription/{project_id}/{role}/user/{user_id}',
            expected_code=200,
            message='subscribe to project',
            func=func,
        )

    def _notification_request(self, project_id, event, body):
        return self._request(
            f'/subscription/{project_id}/{event}',
            expected_code=200,
            message='send notification',
            func=requests.post,
            body=body,
        )

    def subscribe_project_watcher(self, project_id, user_id):
        self._subscription_request(project_id, user_id, 'ProjectWatcher', requests.post)

    def unsubscribe_project_watcher(self, project_id, user_id):
        self._subscription_request(
            project_id, user_id, 'ProjectWatcher', requests.delete
        )

    def subscribe_project_seer(self, project_id, user_id):
        self._subscription_request(project_id, user_id, 'ProjectSeer', requests.post)

    def subscribe_project_seeder(self, project_id, user_id):
        self._subscription_request(project_id, user_id, 'ProjectSeeder', requests.post)

    def subscribe_project_creator(self, project_id, user_id):
        self._subscription_request(project_id, user_id, 'ProjectCreator', requests.post)

    def notify_new_seeder(self, project, user):
        body = {'project': project.name, 'username': user.email.split('@')[0]}
        self._notification_request(project.id, 'NewSeederNotification', body)

    def _notify_new_stage_non_creator(self, project, stage, user):
        body = {
            'project': project.name,
            'stage_number': stage.stage_index,
            'username': user.email.split('@')[0],
        }
        self._notification_request(project.id, 'NewStageNotification_noncreator', body)

    def _notify_new_stage_creator(self, project, stage, user):
        body = {
            'project': project.name,
            'stage_number': stage.stage_index,
            'username': user.email.split('@')[0],
        }
        self._notification_request(project.id, 'NewStageNotification_creator', body)

    def notify_new_stage(self, project, stage, user):
        self._notify_new_stage_non_creator(project, stage, user)
        self._notify_new_stage_creator(project, stage, user)

    def _notify_new_seer_creator(self, project, user):
        body = {'project': project.name, 'username': user.email.split('@')[0]}
        self._notification_request(project.id, 'NewSeer_creator', body)

    def _notify_new_seer_seer(self, project, user):
        body = {
            'project': project.name,
            'username': user.email.split('@')[0],
        }
        self._notification_request(project.id, 'NewSeer_seer', body)

    def notify_new_seer(self, project, user):
        self._notify_new_seer_creator(project, user)
        self._notify_new_seer_seer(project, user)

    def notify_change_state(self, project):
        body = {'project': project.name, 'state': project.current_state.value}
        self._notification_request(project.id, 'ChangeStateNotification', body)


chat_client = ChatClient()
