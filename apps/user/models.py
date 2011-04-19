
import datetime
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor



SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    # not used at the moment
    def activate_user(self, activation_key):
        print "IN ACTIVATE USER"
        print activation_key
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                print "model does not exist"
                return False
            if not profile.activation_key_expired():
                print "here"
                user = profile.user
                print "user: ",
                print user
                user.is_active = True
                user.save()
                print "activation status: ",
                print user.is_active

                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        print "not SHA"
        return False

    def create_inactive_user(self, username, email, password):
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)
        registration_profile.send_activation_email()

        return new_user

    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = sha_constructor(salt+username).hexdigest()
        return self.create(user=user,
                           activation_key=activation_key)

    def delete_expired_users(self):
        for profile in self.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()

class RegistrationProfile(models.Model):
    ACTIVATED = u"ALREADY_ACTIVATED"

    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = "registration profile"
        verbose_name_plural = "registration profiles"
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True

    def send_activation_email(self):
        """
        registration/activation_email.txt
            This template will be used for the body of the email.

        """
        activation_details = { 'activation_key': self.activation_key,
                               'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS }
        print self.activation_key
        subject = "Welcome to OneTree!" # must NOT contain new lines
        
        message = render_to_string('registration/activation_email.txt',
                                   activation_details)
        
        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
