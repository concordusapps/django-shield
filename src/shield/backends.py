# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from .rules import registry


class ShieldBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True

    def authenticate(self, username, password):
        # We don't handle authentication.
        return None

    def has_perm(self, user, perm, obj=None):
        if obj is None:
            # No object; django - you do it
            return False

        if user and not user.is_anonymous() and not user.is_active:
            # inactive and anonymous users never have permissions
            return False

        # retrieve the rule
        rule = registry.get((perm, obj.__class__))
        if rule is None:
            # No rule; no permission
            return False

        # execute the rule and evaluate against the object
        match = rule(user, obj)
        if type(match) is bool:
            return match

        # execute and check for existance
        qset = obj.__class__.objects.filter(rule(user, obj)).filter(pk=obj.pk)
        return qset.exists()

    def has_perms(self, user, perm_list, obj=None):
        if obj is None:
            # No object; django - you do it
            return False

        if user and not user.is_anonymous() and not user.is_active:
            # inactive and anonymous users never have permissions
            return False

        # Iterate through permissions
        result = True
        for perm in perm_list:
            # retrieve the rule
            rule = registry.get((perm, obj.__class__))
            if rule is None:
                # No rule; no permission
                return False

            # execute and check for existance
            # execute the rule and evaluate against the object
            match = rule(user, obj)
            if type(match) is not bool:
                # execute and check for existance
                qset = obj.__class__.objects.filter(rule(user, obj)).filter(
                    pk=obj.pk)
                match = qset.exists()

            # Combine
            result = result and match

        # Return result
        return result

    def objects_for_perm(self, manager, perm, user):
        if user and not user.is_anonymous() and not user.is_active:
            # inactive and anonymous users never have permissions
            return manager.none()

        # retrieve the rule
        rule = registry.get((perm, manager.model))
        if rule is None:
            # No rule; no permission
            return manager.none()

        # execute and retrieve users
        return manager.filter(rule(user, None))

    def objects_for_perms(self, manager, perms, user):
        if user and not user.is_anonymous() and not user.is_active:
            # inactive and anonymous users never have permissions
            return manager.none()

        # retrieve the rules and build the qset
        objects = manager
        for perm in perms:
            rule = registry.get((perm, manager.model))
            if rule is None:
                # No rule; no permission
                return manager.none()

            # Apply rule
            objects = objects.filter(rule(user, None))

        # execute and retrieve users
        return objects
