from django.db import models
from django.forms import ModelForm
from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import PostType
from django.contrib import auth
# from django import forms # for experimentation

'''
I temporarily allowed some of the following fields to be blank. We should
go back through and figure out which ones we actually want to be blank.

We need to add null=True for things that are integers. See "making date
and numeric fields optional" at:

http://www.djangobook.com/en/2.0/chapter06/
'''

# ===============================
# POST
# ===============================

class Post(models.Model):
    origin_group = models.ForeignKey('Group', blank=True, null=True)
    author = models.ForeignKey(auth.models.User, blank=True, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True)
    upvotes = models.IntegerField(blank=True, null=True)
    downvotes = models.IntegerField(blank=True, null=True)
    spamvotes = models.IntegerField(blank=True, null=True)

    post_type = PostType.POST

    '''"Comment List" represented implicitly. Given a post, we should be able
    to get the the associated comments through the foreign key relationship.
    '''

    class Meta:
        abstract = True  # post instances cannot be declared
        ordering = ['-date']

    def score(self):
        return self.upvotes - self.downvotes

    # note that this function is not called in the wall views to sort
    # instead, calc_hot_score from rank_posts is directly called
    def hotscore(self):
        return calc_hot_score(self)

    def __unicode__(self):
        return self.text # temporary since other fields can be blank
        #return "Post by" + self.author + "on" + self.date;

# ===============================
# ANNOUNCEMENT
# ===============================
class Announcement(Post):
    post_type = PostType.ANNOUNCEMENT

# ===============================
# EVENT
# ===============================
class Event(Post):
    event_title = models.CharField(max_length=30)
    event_place = models.CharField(max_length=30)
    event_date = models.DateTimeField()
    event_url = models.CharField(max_length=30, unique=True)
    flags = models.ManyToManyField('Flag')
    post_type = PostType.EVENT

# ===============================
# COMMENT
# ===============================
# We should only associate a comment with either an event or an announcement
# Not both
class Comment(Post):
    announcement = models.ForeignKey('Announcement')
    event = models.ForeignKey('Event')

class Flag(models.Model):
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name;

# ===============================
# GROUP
# ===============================
class Group(models.Model):
    name = models.CharField(max_length=30)
    parent = models.ForeignKey('Group', related_name="child_set", blank=True,
                               null=True)

    users = models.ManyToManyField(auth.models.User, through='Membership', blank=True,
                                    null=True)

    # A group can have many posts. A post can appear on many groups.
    announcements = models.ManyToManyField('Announcement', blank=True, null=True)
    events = models.ManyToManyField('Event', blank=True, null=True)

    #members = models.ManyToManyField('User', through='Membership')
    #admins = models.ManyToManyField('User', through='Administrators')
    #subscribers = models.ManyToManyField('User')
    #email_subscribers = models.ManyToManyField('User')
    
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    groupinfo = models.OneToOneField('GroupInfo', blank=True, null=True)
    url = models.CharField(max_length=30, unique=True)

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

# ===============================
# MEMBERSHIP
# ===============================
class Membership(models.Model):
    user = models.ForeignKey(auth.models.User)
    group = models.ForeignKey('Group')
    is_admin = models.BooleanField()
    is_member = models.BooleanField()
    is_subscriber = models.BooleanField()
    is_email_subscriber = models.BooleanField()

# ===============================
# TAG 
# ===============================
class Tag(models.Model):
    tag = models.CharField(max_length=30)

# ===============================
# GROUPINFO
# ===============================
class GroupInfo(models.Model):
    pass

# ===============================
# USER
# ===============================
'''class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    userinfo = models.OneToOneField('UserInfo', blank=True, null=True) # we can deal with this later...

    # should users specify a username? easy for url creation
    # each user has their own page for future news feeds
    username = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
'''
# ===============================
# USERINFO
# ===============================
class UserInfo(models.Model):
    pass
