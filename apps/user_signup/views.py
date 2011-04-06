from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from OneTree.apps.group_signup.models import DivErrorList

def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, error_class=DivErrorList)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/user/" + new_user.username)
    else:
        form = UserCreationForm(error_class=DivErrorList)
    return render_to_response("base_usersignup.html", {
        'form': form}, RequestContext(request))
