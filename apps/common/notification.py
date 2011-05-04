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
    ''' Afaik recv_user and recv_group will and should not be set for
    the same notification. '''
    
    # use when you want to send a notification to a user
    # receiver can be blank if we send notification to a group instead
    recv_user = models.ForeignKey(auth.models.User, null=True, blank=True,
                                 related_name="recv_notifications")

    # use when you want to send a notification to a group
    # leave blank if you want to send a notification to a user
    recv_group = models.ForeignKey('Group', null=True, blank=True)
    
    sender = models.ForeignKey(auth.models.User, related_name="sent_notifications",
                               null=True, blank=True)
    sender_group = models.ForeignKey('Group', 
                                     related_name="sent_group_notifications", 
                                     null=True, blank=True)

    # notifications that haven't been looked at yet
    new = models.BooleanField(default=True)
    
    # notifications that have been looked at but unanswered
    pending = models.BooleanField(blank=True)
    date = models.DateTimeField(auto_now=True)

    # true if answer was yes, false if it was no
    answered_yes = models.BooleanField(default=False)

    # default values for answer yes and no
    answer_yes = None
    answer_no = None
    
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
            recv = self.recv_user.username
        except AttributeError:
            recv = ''
        try:
            sender = self.sender.username
        except AttributeError:
            sender = ''
            
        return sender + ' request to ' + recv

    def _get_answer_descrip(self):
        return ''
    answer_descrip = property(_get_answer_descrip)

    def not_new(self):
        self.new = False
        self.save()

class Confirmation(Notification):
    text = models.CharField(max_length=300)

    def __init__(self, *args, **kwargs):
        self._meta.get_field('pending').default = False
        super(Confirmation, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return mark_safe(self.text)
        
class MembershipReq(Notification):
    # Parameters that is passed in:
    # - sender=request.user
    # - recv_group=group

    # default values for answer yes and no
    answer_yes = 'Approved'
    answer_no = 'Denied'

    # Initialize - what exactly does this do?
    def __init__(self, *args, **kwargs):
        self._meta.get_field('pending').default = True
        super(MembershipReq, self).__init__(*args, **kwargs)

    # get URL link of the group (for use in template)
    def get_group_link(self):
        url = self.recv_group.full_url
        recv_group_with_url = '<a href="' + url + '">' + self.recv_group.name + '</a>'
        return recv_group_with_url

    # Confirmation message
    def send_confirmed(self):
        confirm_text = 'You have been confirmed as a member of ' + self.get_group_link()
        confirm = Confirmation(recv_user=self.sender, text=confirm_text)
        confirm.save()

    # Handle approval
    def handle_yes(self):
        self.sender.get_profile().memberships.add(self.recv_group)
        self.send_confirmed()
        self.pending = False
        self.answered_yes = True
        self.save()

    # Handle disapproval
    def handle_no(self):
        self.pending = False
        self.answered_no = False
        self.save()

    # Approved/Disapproved Text
    def _get_answer_descrip(self):
        if not self.pending:
            if self.answered_yes:
                return answer_yes
            else:
                return answer_no
    answer_descrip = property(_get_answer_descrip)
    
    # Unicode for printing
    # we need to make sure users don't put javascript in the url, because
    # i'm going to unescape this
    def __unicode__(self):
        try:
            sender = self.sender.username
        except AttributeError:
            sender = ''        
        req_text = sender + ' has requested to be a member of ' + self.get_group_link()
        return mark_safe(req_text)
    
class ParentReq(Notification):
    # Parameters that are passed in:
    # - sender_group = requesting_child
    # - recv_group = pending_parent

    # Initialize
    def __init__(self, *args, **kwargs):
        self._meta.get_field('pending').default = True
        super(ParentReq, self).__init__(*args, **kwargs)


    # Get URL link of parent group
    def get_group_link(self):
        url = self.recv_group.full_url
        recv_group_with_url = '<a href="' + url + '">' + self.recv_group.name + '</a>'
        return recv_group_with_url

    def get_sender_group_link(self):
        url = self.sender_group.full_url
        sender_group_with_url = '<a href="' + url + '">' + self.sender_group.name + '</a>'
        return sender_group_with_url

    # Confirmation message
    def send_confirmed(self):
#        confirm_text = self.get_childgroup_link()
        confirm_text =  'Group ' + self.get_sender_group_link() + ' is now a child of ' + self.get_group_link()
        confirm = Confirmation(recv_group=self.sender_group, 
                               text=confirm_text)
        confirm.save()
        
    # Handle approval
    def handle_yes(self):
        self.sender_group.parent=self.recv_group
        self.send_confirmed()
        self.pending = False
        self.answered_yes = True
        self.sender_group.save() # this is needed & different from the save() below
        self.save()

    # Handle disapproval
    def handle_no(self):
        self.pending = False
        self.answered_no = False
        self.save()

    # Approved/Disapproved Text
    def _get_answer_descrip(self):
        if not self.pending:
            if self.answered_yes:
                return 'Approved'
            else:
                return 'Denied'
    answer_descrip = property(_get_answer_descrip)
    
    # Unicode for printing, etc
    # we need to make sure users don't put javascript in the url, because
    # i'm going to unescape this
    def __unicode__(self):
        try:
            sender = self.sender_group.name
        except AttributeError:
            sender = ''        
        req_text = "Group " + self.get_sender_group_link() + ' has requested to be a child of ' + self.get_group_link()
        return mark_safe(req_text)
    
