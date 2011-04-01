from django.db import models
from django.forms import ModelForm
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
    author = models.ForeignKey('User', blank=True, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now=True)
    upvotes = models.IntegerField(blank=True, null=True)
    downvotes = models.IntegerField(blank=True, null=True)
    spamvotes = models.IntegerField(blank=True, null=True)

    '''"Comment List" represented implicitly. Given a post, we should be able
    to get the the associated comments through the foreign key relationship.
    '''

    class Meta:
        abstract = True  # post instances cannot be declared
        ordering = ['-date']

    def __unicode__(self):
        return self.text; # temporary since other fields can be blank
        #return "Post by" + self.author + "on" + self.date;

# ===============================
# ANNOUNCEMENT
# ===============================
class Announcement(Post):
    pass

# ===============================
# EVENT
# ===============================
class Event(Post):
    eventDate = models.DateTimeField()    
    flags = models.ManyToManyField('Flag')


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
    users = models.ManyToManyField('User', through='Membership', blank=True,
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
    url = models.CharField(max_length=30)

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

class Group(ModelForm):
    class Meta:
        model = Group

# ===============================
# MEMBERSHIP
# ===============================
class Membership(models.Model):
    user = models.ForeignKey('User')
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
class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    userinfo = models.OneToOneField('UserInfo')

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

# ===============================
# USERINFO
# ===============================
class UserInfo(models.Model):
    pass

