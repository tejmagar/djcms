from ..models import StatusMixin


class StatusAction:
    def __init__(self, instance: StatusMixin):
        self.instance = instance

    def _action_trash(self):
        self.instance.is_trash = True
        self.instance.save()

    def _action_restore(self):
        self.instance.is_trash = False
        self.instance.save()

    def _action_delete(self):
        self.instance.delete()

    def perform(self, action_type: str) -> bool:
        """
        If any of the action is performed return True
        """
        
        actions = {
            'trash': self._action_trash,
            'restore': self._action_restore,
            'delete': self._action_delete
        }

        action = actions.get(action_type, None)
        if action:
            action()
            return True

        return False
