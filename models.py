from django.db import models

class Post(models.Model):
    group = models.ForeignKey(Group)
    author = models.ForeignKey(User)
    text = models.TextField()
    date = models.DateField(auto_now=True)
    upvotes = models.IntegerField() 
    downvotes = models.IntegerField() 
    spamvotes = models.IntegerField() 

    '''"Comment List" represented implicitly. Given a post, we should be able
    to get the the associated comments through the foreign key relationship.
    '''

    class Meta:
        abstract = True  # post instances cannot be declared

    def __unicode__(self):
        return "Post by" + self.author + "on" + self.date;

class Announcement(models.Post):
    pass

class Event(models.Post):
    eventDate = models.DateField()    
    flags = models.ManyToManyField(Flag)

# We should only associate a comment with either an event or an announcement
# Not both
class Comment(models.Post):
    announcement = models.ForeignKey(Announcement)
    event = models.ForeignKey(Event)

class Flag(models.Model):
    name = models.charField(max_length=30)
    
    def __unicode__(self):
        return self.name;

class Group(models.Model):
    name = models.CharField(max_length=30)
    parent = models.ForeignKey(Group, related_name="child_set")
    posts = models.ManyToManyField(Post)
    members = models.ManyToManyField(User)
    admins = models.ManyToManyField(User)
    subscribers = models.ManyToManyField(User)
    email_subscribers = models.ManyToManyField(User)
    tags = models.ManyToManyField(Tag)
    groupinfo = models.OneToOneField(GroupInfo)

    '''Announcements, Events represented through foreignKey relationship.'''

class GroupInfo(models.Model):
    pass

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    userinfo = models.OneToOneField(UserInfo)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class UserInfo(models.Model):
    pass
