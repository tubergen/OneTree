from django.db import models
from django.forms import ModelForm
from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import *
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models.signals import post_save
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
    #tags?
#    TAG_CHOICES = (
#        (u'D', u'Dance'),
#        (u'S', u'Singing'),
#        (u'A', u'Athletics'),
#    )

    name = models.CharField(max_length=30, verbose_name="name")
    parent = models.ForeignKey('Group', related_name="child_set", blank=True,
                               null=True, verbose_name="parent")

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

                    
# ===============================
# USER PROFILE
# ===============================
class UserProfile(models.Model):
    user = models.ForeignKey(User)
    subscriptions = models.ManyToManyField('Group', related_name='subscribers', blank=True)
    memberships = models.ManyToManyField('Group', related_name='members', blank=True)
    #administrations = models.ManyToManyField('Group', related_name='administers', blank=True)

    # maybe condense these into two pairs into two models with a through?
    removed_events = models.ManyToManyField('Event', blank=True)
    removed_anns = models.ManyToManyField('Announcement', blank=True)

    voted_events = models.ManyToManyField('Event', related_name='voted_user_set',
                                          through='EventVote', blank=True)
    voted_anns = models.ManyToManyField('Announcement', related_name='voted_user_set',
                                       through='AnnVote', blank=True)    
    
    def __unicode__(self):
        return "%s's profile" % self.user

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            profile, created = UserProfile.objects.get_or_create(user=instance)

    post_save.connect(create_user_profile, sender=User)

    '''
    Changes the subscription status of this profile's user for the
    specified group. If the user is already subscribed, he is
    unsubscribed. If not subscribed, he is subscribed.
    '''
    def change_subscribe(self, group_id):
        sub_manager = self.subscriptions;

        print "a"
        
        # check to see if user is already subscribed
        try:
            subscribed_group = sub_manager.get(id=group_id)
        except Group.DoesNotExist:
            subscribed_group = None

        group = Group.objects.get(id=group_id)
        if subscribed_group == None: # then subscribe the user
            sub_manager.add(group)
        else:                        # then unsubscribe the user
            sub_manager.remove(group)

    '''
    Removes the post specified by post_id from this profile's newsfeed.
    Returns True if removal is successful. Returns False otherwise.
    '''
    def remove_post(self, post_id, post_type):
        err_loc = ' See remove_post in the UserProfile model.'
        
        try: 
            if post_type == PostType.EVENT:
                post = Event.objects.get(id=post_id)
                self.removed_events.add(post)
            elif post_type == PostType.ANNOUNCEMENT:
                post = Announcement.objects.get(id=post_id)
                self.removed_anns.add(post)                    
            else:
                print 'Tried to delete non-announcement non-event.' + err_loc
                return False

            return True

        except ObjectDoesNotExist:
            print 'Error: Tried to delete non-existent object.' + err_loc
            return False


    def change_vote(self, user, post_id, post_type, vote_type):
        err_loc = ' See change_vote in the UserProfile model.'

        # testing crap, can ignore
        '''
        ann = Announcement()
        ann.text="yoyo"
        ann.save()
        print ann.id
        #av = AnnVote.objects.create(ann=ann, user_profile=user.get_profile(), vote=1)
        #av.save()
        #user.get_profile().voted_anns.add(ann)
        #user.get_profile().voted_anns.save()
        try:
            print user.get_profile().annvote_set.get(user_profile=user.get_profile(), ann=ann).vote
        except AnnVote.DoesNotExist:
            pass
        '''
        
        profile = user.get_profile()
        if post_type == PostType.EVENT:
            try:
                post_vote = profile.annvote_set.get(user_profile=profile, ann=ann)
            except EventVote.DoesNotExist:                
                post_vote = AnnVote.objects.create(ann=ann, user_profile=profile,
                                                   vote=vote_type)
                post_vote.save()
                return True
        elif post_type == PostType.ANNOUNCEMENT:
            try:
                post_vote = profile.annvote_set.get(user_profile=profile, ann=ann)
            except AnnVote.DoesNotExist:                
                post_vote = AnnVote.objects.create(ann=ann, user_profile=profile,
                                                   vote=vote_type)
                post_vote.save()
                return True
        else:
            print 'Tried to vote on non-announcement non-event.' + err_loc
            return False

        # update the actual vote
        post_vote.vote = vote_type
        post_vote.save()
        return True

    '''
    Returns 'up' if the user's most recent vote on this post was up,
    down if it was down, and None if the user hasn't voted before.
    '''
    def get_vote(self, user, post_id, post_type):
        err_loc = ' See get_vote in the UserProfile model.'        
        if post_type == PostType.EVENT:
            try:
                return profile.annvote_set.get(user_profile=profile, ann=ann).vote
            except EventVote.DoesNotExist:                
                return None
        elif post_type == PostType.ANNOUNCEMENT:
            try:
                return profile.annvote_set.get(user_profile=profile, ann=ann).vote
            except AnnVote.DoesNotExist:                
                return None
        else:
            print 'Cannot vote on non-announcement non-event.' + err_loc
            return None


# ===============================
# EventVote
# ===============================
class EventVote(models.Model):
    user_profile = models.ForeignKey('UserProfile');
    event = models.ForeignKey('Event');
    # 0 => has not voted, 1 => up voted, 2 => down voted
    vote = models.IntegerField()

# ===============================
# AnnVote
# ===============================
class AnnVote(models.Model):
    user_profile = models.ForeignKey('UserProfile');
    ann = models.ForeignKey('Announcement');
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
    tag = models.CharField(max_length=30)

# ===============================
# GROUPINFO
# ===============================
class GroupInfo(models.Model):
    pass

# ===============================
# USER
# ===============================

# See user_signup/models.py for user model


# ===============================
# USERINFO
# ===============================
class UserInfo(models.Model):
    pass

class Test(models.Model):
    pass
