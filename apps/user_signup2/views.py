from OneTree.apps.user_signup.models import UserForm, DivErrorList
from django.template import RequestContext

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response


# REFERENCES:
# http://docs.djangoproject.com/en/dev/topics/forms/modelforms/
#     the above one has info on changing existing objects
#     that should be useful later on when editing content.
# http://docs.djangoproject.com/en/dev/topics/forms/
# http://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, error_class=DivErrorList)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/user/temporary")
    else:
        form = UserCreationForm()
    return render_to_response("base_usersignup.html", {
            'form': form, }, RequestContext(request)
    )



def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, error_class=DivErrorList) # Form bound to POST data
        if form.is_valid():    # Add validation
            form.save()

            #first_name = form.cleaned_data['first_name']
            #last_name = form.cleaned_data['last_name']
            #email = form.cleaned_data['email']

            # necessary?
            
            # where should this redirect to? user info page?
            return HttpResponseRedirect('/user/' + form.cleaned_data['username'])

        else:
            return render_to_response('base_usersignup.html', {'form': form, 'is_first_attempt': False,}, RequestContext(request)) # change redirect destination

    else:
        form = UserForm(error_class=DivErrorList) # An unbound form - can use this for error messages
    return render_to_response('base_usersignup.html', {'form': form, 'is_first_attempt': True,}, RequestContext(request))
