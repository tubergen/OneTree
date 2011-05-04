from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import PostType, VoteType
from django.db import models
from django.forms import ModelForm
from django.contrib import auth
from django.db.models.signals import post_save
# from django import forms # for experimentation
from itertools import chain
from OneTree.apps.user.models import RegistrationProfile
from django import forms
from django.forms.util import ErrorList
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
import os



group_url = "/group/"

# ===============================
# GROUP
# ===============================
class Group(models.Model):

    name = models.CharField(max_length=15, verbose_name="name", unique=True)
    parent = models.ForeignKey('Group', related_name="child_set", blank=True,
                               null=True, verbose_name="parent")
    toplevelgroup = models.BooleanField()
    inactive_child = models.ManyToManyField('Group', related_name="inactive_c",
                                            blank=True, null=True)
    # profile picture
    #img = models.CharField(max_length=50, null=True, blank=True)

    def profile_location(self, filename):
        return os.path.join('uploaded_files', str(self.url),
                            'profile', filename)

    img = models.ImageField(upload_to=profile_location, blank=True, null=True)

    # A group can have many posts. A post can appear on many groups.
    announcements = models.ManyToManyField('Announcement', blank=True, null=True)
    events = models.ManyToManyField('Event', blank=True, null=True)

    #members = models.ManyToManyField('User', through='Membership')
    admins = models.ManyToManyField(auth.models.User, related_name='admin_groups')
    superadmins = models.ManyToManyField(auth.models.User, related_name='superadmin_groups')
    #subscribers = models.ManyToManyField('User')
    #email_subscribers = models.ManyToManyField('User')
    
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    # bridge b/t group and tags?
    keywords = models.CharField(max_length=30, blank=True, null=True, help_text="Used for search results")
    url = models.SlugField(max_length=30, 
                           unique=True, 
                           verbose_name=(group_url),)

    def _get_full_url(self):
        return group_url + self.url
    full_url = property(_get_full_url)

    def addAdmin(self, user):
        self.admins.add(user)
            
    def addSuperAdmin(self, user):
        self.superadmins.add(user)


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
        
   # def profile_location(self, filename):
   #     return os.path.join('uploaded_files', str(self.url),
   #                         'profile', filename)
        

    def __unicode__(self):
        return self.name;

#    def getPhoto(self, x):
#        photo = self.photos[x]
#        return re.sub("\W+", "", photo.lower())
#        return str(self.photos[x])

# Create your models here.
class GroupForm(ModelForm):

    # Parent as CharField (Comment out to revert back to dropdown menu)
#    parent = forms.CharField()


    print "========= GroupForm ============="



    def clean_parent(self):
        print "STATUS > running clean_parent"
        data = self.cleaned_data['parent']
        if data is None:
            raise forms.ValidationError("You are an orphaned group =[ Please specify a parent?")
        print "STATUS > printing cleaned_parent data: "

        try:
            parentgroup = Group.objects.get(name=data)
        except:
            raise forms.ValidationError("Specified parent does not exist")

        return parentgroup


    parent = models.ForeignKey('Group', related_name="child_set", blank=False,
                               null=False, verbose_name="parent")
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Group
        fields = ('name', 'parent', 'url', 'keywords', ) # tags removed
