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
from OneTree.apps.common.group import Group
from OneTree.apps.common.notification import *
# more imports at bottom

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

    '''
    Changes this post's upvote or downvote score by amount.
    Amount must be either 1 or -1 for function to have an effect.
    '''
    def update_vote(self, vote_type, amount):
        err_loc = ' Error occured at update_vote() in model Post.'
    
        if amount == None or amount == 0:
            return

        if amount != -1 and amount != 1:
            print 'Error: amount not -1 or 1.' + err_loc
        if vote_type == VoteType.UP:
            if self.upvotes == None:
                self.upvotes = amount
            else:
                self.upvotes += amount
        elif vote_type == VoteType.DOWN:
            if self.downvotes == None:
                self.downvotes = amount
            else:
                self.downvotes += amount
        else:
            print 'Error: invalid vote type.' + err_loc
        self.save()
   
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
class Comment(Post):
    announcement = models.ForeignKey('Announcement', blank=True, null=True)
    event = models.ForeignKey('Event', blank=True, null=True)
    parent_comment = models.ForeignKey('Comment', blank=True, null=True)
    # only one of these three should be true... this is a stupid way to do it.
    # can we somehow access any Posts? maybe we really should just combine them
    # all
    
    level = models.IntegerField()
    removed = models.BooleanField(default=False)
    post_type = PostType.COMMENT
    # we may change post text if it's inappropriate, but comment_text saves
    # the text the user entered
    comment_text = models.TextField(default=None)

    # i hope this works ...
    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        #self._meta.get_field('comment_text').default = self.text
        if self.comment_text == None:
            self.comment_text = self.text
            self.save()
        
class Flag(models.Model):
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name;


# ===============================
# EventVote
# ===============================
class EventVote(models.Model):
    user_profile = models.ForeignKey('UserProfile');
    post = models.ForeignKey('Event');
    # 0 => has not voted, 1 => up voted, 2 => down voted
    vote = models.IntegerField()

# ===============================
# AnnVote
# ===============================
class AnnVote(models.Model):
    user_profile = models.ForeignKey('UserProfile');
    post = models.ForeignKey('Announcement');
    # 0 => has not voted, 1 => up voted, 2 => down voted
    vote = models.IntegerField()

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
    tag = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return self.tag

# OTHER -- WE MAY OR MAY NOT WANT TO PUT THIS HERE?
class GroupInfo(models.Model):
    group = models.ForeignKey('Group')
    data = models.TextField()
    # blurb should be what data is now
    # blurb = models.CharField(max_length=50)
    
    # pass
    
class UserInfo(models.Model):
    pass

# this has dependencies on models in here, so it needs to be at bottomx
from OneTree.apps.common.user import UserProfile
