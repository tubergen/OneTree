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
    pending = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)    

    '''
    These handle_yes/no methods are just debug functions that subclasses
    should override.
    '''
    def handle_yes(self):
        self.pending = False
        self.save()

    def handle_no(self):
        self.pending = False
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
    def __init__(self, *args, **kwargs):
        self._meta.get_field('pending').default = True
        super(MembershipReq, self).__init__(*args, **kwargs)
        
    def handle_yes(self):
        self.sender.get_profile().memberships.add(self.group)
        # send the sender a "you were accepted" notification
        self.pending = False
        self.save()

    def handle_no(self):
        self.pending = False
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
    
