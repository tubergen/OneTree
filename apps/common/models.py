from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import PostType, VoteType
from django.db import models
from django.forms import ModelForm
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# from django import forms # for experimentation
from itertools import chain
from OneTree.apps.user_signup.models import RegistrationProfile


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

    post_type = PostType.COMMENT

class Flag(models.Model):
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name;




# ===============================
# GROUP
# ===============================
class Group(models.Model):

    name = models.CharField(max_length=30, verbose_name="name", unique=True)
    inactive_parent = models.ForeignKey('Group', related_name="inactive_children",
                                        blank=True, unique=True, null=True)
    parent = models.ForeignKey('Group', related_name="child_set", blank=True,
                               null=True, unique=True, verbose_name="parent")

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
    groupinfo = models.OneToOneField('GroupInfo', blank=True, null=True)
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

# ===============================
# USER PROFILE
# ===============================
class UserProfile(models.Model):
    user = models.ForeignKey(auth.models.User)
    subscriptions = models.ManyToManyField('Group', related_name='subscribers', blank=True)
    memberships = models.ManyToManyField('Group', related_name='members', blank=True)
    #administrations = models.ManyToManyField('Group', related_name='administers', blank=True)

    # maybe condense these into two pairs into two models with a through?
    removed_events = models.ManyToManyField('Event', blank=True)
    removed_anns = models.ManyToManyField('Announcement', blank=True)

    voted_events = models.ManyToManyField('Event', related_name='voted_event_user_set',
                                          through='EventVote', blank=True)
    voted_anns = models.ManyToManyField('Announcement', related_name='voted_ann_user_set',
                                       through='AnnVote', blank=True)    
    
    def __unicode__(self):
        return "%s's profile" % self.user

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            profile, created = UserProfile.objects.get_or_create(user=instance)

    post_save.connect(create_user_profile, sender=auth.models.User)

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


    '''
    Changes the profile's vote for the post specified based on a click of
    type vote_type (ie: up or down), taking into account the current state.
    
    Creates the [PostType]Vote object if it doesn't already exist.

    Returns a tuple (up_score_change, down_score_change), which indicates to
    the caller how these scores ought to change.
    
    Returns None, None if there's an error.
    '''
    def change_vote(self, post_id, post_type, vote_type):
        err_loc = ' See change_vote in the UserProfile model.'

        print post_type

        # get the vote, being careful to make sure the [PostType]Vote object exists
        if post_type == PostType.EVENT:
            this_event = Event.objects.get(id=post_id)
            try:
                post_vote = self.eventvote_set.get(user_profile=self, post=this_event)
                if post_vote.vote != VoteType.NONE:
                    already_voted = True
                else:
                    already_voted = False
            except EventVote.DoesNotExist:
                post_vote = EventVote.objects.create(user_profile=self, post=this_event,
                                                     vote=VoteType.NONE)
                already_voted = False
        elif post_type == PostType.ANNOUNCEMENT:
            this_ann = Announcement.objects.get(id=post_id)
            try:
                post_vote = self.annvote_set.get(user_profile=self, post=this_ann)
                if post_vote.vote != VoteType.NONE:
                    already_voted = True
                else:
                    already_voted = False
            except AnnVote.DoesNotExist:
                post_vote = AnnVote.objects.create(user_profile=self, post=this_ann, 
                                                   vote=VoteType.NONE)
                already_voted = False
        else:
            print 'Tried to vote on non-announcement non-event.' + err_loc
            return None, None

        # first check if this is an "unselect vote" click
        if post_vote.vote == vote_type:
            post_vote.vote = VoteType.NONE # no vote is selected
            post_vote.save()
            if vote_type == VoteType.UP:
                return (-1, 0)
            elif vote_type == VoteType.DOWN:
                return (0, -1)
            else:
                print 'Invalid Vote Type.' + err_loc
                return None, None

       
        # it's not an "unselect" click, so update the vote and figure out the
        # the return value

        # not an unselect, so update the actual vote
        post_vote.vote = vote_type
        post_vote.save()

        # figure out the return value
        if vote_type == VoteType.UP:
            if already_voted == True:
                return (1, -1)
            else:
                return (1, 0)
        if vote_type == VoteType.DOWN:
            if already_voted == True:
                return (-1, 1)
            else:
                return (0, 1)

    '''
    Returns the set of voted_events chained with the list of voted announcements
    For efficiency, we may ultimately want to only return the first X members
    of these sets, which will be the ones displayed on the page.
    '''
    def get_voted_posts(self, group=None):
        if group:
            announcements = group.announcements.all()
            events = group.events.all()
            relevant_events = self.eventvote_set.filter(post__in=events)
            relevant_anns = self.annvote_set.filter(post__in=announcements)
            return list(chain(relevant_anns, relevant_events));
        else:
            # not sure if list() is necessary
            return list(chain(self.annvote_set.all(), self.eventvote_set.all()));

    '''
    Returns the  user's last vote, or None if the user hasn't voted before.
    Nothing calls this method as of 4/13/10. It's untested.
    '''
    def get_vote(self, post_id, post_type):
        print 'here'
        err_loc = ' See get_vote in the UserProfile model.'        
        if post_type == PostType.EVENT:
            try:
                return self.eventvote_set.get(user_profile=self, post=ann).vote
            except EventVote.DoesNotExist:                
                return None
        elif post_type == PostType.ANNOUNCEMENT:
            try:
                return self.annvote_set.get(user_profile=self, post=ann).vote
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
