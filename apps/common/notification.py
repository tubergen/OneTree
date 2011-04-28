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
    # here we will send notifcation to all admins of group; this should probably
    # be called "receiving group" or something
    group = models.ForeignKey('Group', null=True, blank=True)
    
    sender = models.ForeignKey(auth.models.User, related_name="sent_notifications",
                               null=True, blank=True)
    pending = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    answer_descrip = models.CharField(max_length=50)

    class Meta:
        ordering = ['-date']

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

class Confirmation(Notification):
    text = models.CharField(max_length=300)

    def __init__(self, *args, **kwargs):
        self._meta.get_field('pending').default = False
        super(Confirmation, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return mark_safe(self.text)
        
class MembershipReq(Notification):
    def __init__(self, *args, **kwargs):
        self._meta.get_field('pending').default = True
        super(MembershipReq, self).__init__(*args, **kwargs)

    def get_group_link(self):
        url = self.group.full_url
        group_with_url = '<a href="' + url + '">' + self.group.name + '</a>'
        return group_with_url

    def send_confirmed(self):
        confirm_text = 'You have been confirmed as a member of ' + self.get_group_link()
        confirm = Confirmation(receiver=self.sender, text=confirm_text)
        confirm.save()
        
    def handle_yes(self):
        self.sender.get_profile().memberships.add(self.group)
        self.send_confirmed()
        self.pending = False
        self.answer_descrip = "Approved"
        self.save()

    def handle_no(self):
        self.pending = False
        self.answer_descrip = "Denied"        
        self.save()

    # we need to make sure users don't put javascript in the url, because
    # i'm going to unescape this
    def __unicode__(self):
        try:
            sender = self.sender.username
        except AttributeError:
            sender = ''        
        req_text = sender + ' has requested to be a member of ' + self.get_group_link()
        return mark_safe(req_text)
    
