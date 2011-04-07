
import datetime
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

def create_profile(user):
    """
    Create a ``RegistrationProfile`` for a given
    ``User``, and return the ``RegistrationProfile``.
    
    The activation key for the ``RegistrationProfile`` will be a
    SHA1 hash, generated from a combination of the ``User``'s
    username and a random salt.
    
    """
    salt = sha_constructor(str(random.random())).hexdigest()[:5]
    username = user.username
    if isinstance(username, unicode):
        username = username.encode('utf-8')
    activation_key = sha_constructor(salt+username).hexdigest()
    return self.create(user=user,
                       activation_key=activation_key)


def create_inactive_user(username, email, password,
                         site, send_email=True):
        """
        Create a new, inactive ``User``, generate a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.
        
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user
    create_inactive_user = transaction.commit_on_success(create_inactive_user)
