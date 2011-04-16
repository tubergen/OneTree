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

