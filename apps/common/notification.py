from django.db import models
from OneTree.apps.common.group import Group
from django.utils.safestring import mark_safe
from django.contrib import auth
from OneTree.apps.common.inheritance import InheritanceCastModel

'''
NOTE: Receiver and group should NOT both be set on the same object, but
one of them SHOULD be set.
'''
class Notification(InheritanceCastModel):
    # receiver can be blank if we send notification to a group instead
    receiver = models.ForeignKey(auth.models.User, null=True, blank=True,
                                 related_name="recv_notifications")
    # here we will send notifcation to all admins of group
    group = models.ForeignKey('Group', null=True, blank=True)
    sender = models.ForeignKey(auth.models.User, related_name="sent_notifications")
    new = models.BooleanField(default=True)

    '''
    These handle_yes/no methods are just debug functions that subclasses
    should override.
    '''
    def handle_yes(self):
        self.new = False
        self.save()

    def handle_no(self):
        self.new = False
        self.save()
    
    def __unicode__(self):
        try:
            recv = self.receiver.username
        except AttributeError:
            recv = ''
        try:
            sender = self.sender.username
        except AttributeError:
            sender = ''
            
        return sender + ' request to ' + recv
    
class MembershipReq(Notification):
    def handle_yes(self):
        self.sender.get_profile().memberships.add(self.group)
        # send the sender a "you were accepted" notification
        self.new = False
        self.save()

    def handle_no(self):
        self.new = False
        self.save()

    # we need to make sure users don't put javascript in the url, because
    # i'm going to unescape this
    def __unicode__(self):
        try:
            sender = self.sender.username
        except AttributeError:
            sender = ''        

        url = self.group.full_url
        group_with_url = '<a href="' + url + '">' + self.group.name + '</a>'
        req_text = sender + ' has requested to be a member of ' + group_with_url
        return mark_safe(req_text)
    