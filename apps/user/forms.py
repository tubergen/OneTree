from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import authenticate


# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = {'class': 'required'}

class ActivationForm(forms.Form):
    username = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
                                label="Your Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                               label="Password")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct username and password. Note that both fields are case-sensitive.")

        return self.cleaned_data

class RegistrationForm(forms.Form):
    """
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    
    """
    username = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
                                label="Your Email")
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
                              label="Re-enter Email")
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label="Password (again)")
    
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("A user with that username already exists.")



    def clean(self):
        if 'username' in self.cleaned_data and 'email' in self.cleaned_data:
            if self.cleaned_data['username'] != self.cleaned_data['email']:
                raise forms.ValidationError("Your email fields didn't match.")

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data

#    def clean_email(self):
#        if User.objects.filter(email__iexact=self.cleaned_data['email']):
#            raise forms.ValidationError("This email address is already in use. Please supply a different email address.")
#        return self.cleaned_data['email']


# Future addition: Agreeing to the site's Terms of Service
class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=u'I have read and agree to the Terms of Service',
                             error_messages={'required': "You must agree to the terms to register"})

