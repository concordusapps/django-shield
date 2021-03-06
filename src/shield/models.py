from django.db.models import manager
from django.db.models.query import QuerySet
from django.contrib import auth


def for_perm(self, perm, user):
    for backend in auth.get_backends():
        if hasattr(backend, "objects_for_perm"):
            return backend.objects_for_perm(self, perm, user)

    return self.none()


def for_perms(self, perms, user):
    for backend in auth.get_backends():
        if hasattr(backend, "objects_for_perm"):
            return backend.objects_for_perms(self, perms, user)

    return self.none()


# Massive hacks beware...
# Waiting on a PR to django to remove this file
if not hasattr(manager.Manager, 'for_perm'):
    setattr(manager.Manager, 'for_perm', for_perm)
    setattr(manager.Manager, 'for_perms', for_perms)
    setattr(QuerySet, 'for_perm', for_perm)
    setattr(QuerySet, 'for_perms', for_perms)
