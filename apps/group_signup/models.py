from django.db import models
from django.forms import ModelForm
from django import forms # for experimentation
from OneTree.apps.common.models import Group
from django.forms.util import ErrorList

class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])

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
