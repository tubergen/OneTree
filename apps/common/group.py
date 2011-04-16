from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import PostType, VoteType
from django.db import models
from django.forms import ModelForm
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# from django import forms # for experimentation
from itertools import chain
from OneTree.apps.user.models import RegistrationProfile

from django import forms
from django.forms.util import ErrorList

# ===============================
# GROUP
# ===============================
class Group(models.Model):

    name = models.CharField(max_length=30, verbose_name="name", unique=True)
    inactive_parent = models.ForeignKey('Group', related_name="inactive_children",
                                        blank=True, unique=True, null=True)
    parent = models.ForeignKey('Group', related_name="child_set", blank=True,
                               null=True, verbose_name="parent")

    users = models.ManyToManyField(auth.models.User, through='Membership', 
                                   blank=True, null=True, related_name='users')

    # A group can have many posts. A post can appear on many groups.
    announcements = models.ManyToManyField('Announcement', blank=True, null=True)
    events = models.ManyToManyField('Event', blank=True, null=True)

    #members = models.ManyToManyField('User', through='Membership')
    admins = models.ManyToManyField(auth.models.User, related_name='admins')
    #subscribers = models.ManyToManyField('User')
    #email_subscribers = models.ManyToManyField('User')
    
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    # bridge b/t group and tags?
    keywords = models.CharField(max_length=30, blank=True, null=True)
    url = models.SlugField(max_length=30, 
                           unique=True, 
                           verbose_name="onetree.princeton.edu/group/", 
                           )


    def addAdmin(self, user):
        curNode = self
        curNode.admins.add(user)
            

    # in future, change this so that parent can 'reject' percolating posts
    def addAnnToParent(self, announcement):
        curNode = self
        while (curNode is not None):
            curNode.announcements.add(announcement)
            curNode = curNode.parent

    def addEventToParent(self, event):
        curNode = self
        while (curNode is not None):
            curNode.events.add(event)
            curNode = curNode.parent

    def add_inactive_parent(self, parent):
        curNode = self
        curNode.inactive_parent.add(parent)
        



    def __unicode__(self):
        return self.name;




# Create your models here.
class GroupForm(ModelForm):
#    def is_valid(self):
#        if 'url' in self and 'name' in self and 'parent' in self:
#            return True
#        return False
#
# do we have to do this? it seems like it validates already...
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Group
        fields = ('name', 'parent', 'url', 'keywords', ) # tags removed


       
