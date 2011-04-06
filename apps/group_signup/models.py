from django.db import models
from django.forms import ModelForm
from django import forms
from OneTree.apps.common.models import Group
from django.forms.util import ErrorList

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
        fields = ('name', 'parent', 'url',)
