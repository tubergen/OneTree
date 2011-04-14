from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import PostType, VoteType
from django.db import models
from django.forms import ModelForm
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# from django import forms # for experimentation
from itertools import chain

class NGroupManager(models.Manager):
    pass
        

# ===============================
# GROUP
# ===============================
class NGroup(models.Model):
    #tags?
#    TAG_CHOICES = (
#        (u'D', u'Dance'),
#        (u'S', u'Singing'),
#        (u'A', u'Athletics'),
#    )

    name = models.CharField(max_length=30, verbose_name="name")
    parent = models.ForeignKey(self, related_name="child_set", blank=True,
                               null=True, verbose_name="parent")
## through=membership deleted
    users = models.ManyToManyField(auth.models.User,  blank=True,
                                    null=True)

    # A group can have many posts. A post can appear on many groups.
    announcements = models.ManyToManyField('Announcement', blank=True, null=True)
    events = models.ManyToManyField('Event', blank=True, null=True)

    tags = models.ManyToManyField('Tag', blank=True, null=True)
    groupinfo = models.OneToOneField('GroupInfo', blank=True, null=True)
    url = models.SlugField(max_length=30, 
                           unique=True, 
                           verbose_name="onetree.princeton.edu/group/", 
                           )

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

    def __unicode__(self):
        return self.name;
