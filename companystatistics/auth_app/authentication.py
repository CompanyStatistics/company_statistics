from .models import CSUser


class EmailAuthBackend(object):
    """
    Authenticate using an e-mail address.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = CSUser.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except CSUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CSUser.objects.get(pk=user_id)
        except CSUser.DoesNotExist:
            return None
