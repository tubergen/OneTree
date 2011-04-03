from django.db import models
from django.forms import ModelForm
from django import forms # for experimentation?
from OneTree.apps.common.models import User
from django.forms.util import ErrorList

class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self:return u''
        return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])

# Create your models here.
class UserForm(ModelForm):
#    def is_valid(self):
#        if 'first_name' in self and 'last_name' in self and 'email' in self:
#            return True
#        return False

# validating ?

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',)
