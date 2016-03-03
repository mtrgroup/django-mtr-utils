from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.backends import ModelBackend, get_user_model

UserModel = get_user_model()


def user_by_id_key(user_id):
    return 'auth:user_by_id.{}'.format(user_id)


class CachedModelBackend(ModelBackend):

    """Default ModelBackend with caching groups, permissions and user model"""

    def get_user(self, user_id):
        key = user_by_id_key(user_id)
        user = cache.get(key)

        if user is not None:
            return user

        try:
            user = UserModel._default_manager \
                .prefetch_related('groups', 'permissions') \
                .get(pk=user_id)
        except UserModel.DoesNotExist:
            user = None

        if user is not None:
            cache.set(key, user)

        return user


def expire_user_by_id(sender, **kwargs):
    user = kwargs['instance']
    cache.delete(user_by_id_key(user.id))
post_save.connect(expire_user_by_id, UserModel)
post_delete.connect(expire_user_by_id, UserModel)
