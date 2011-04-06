from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/user/" + new_user.username)
    else:
        form = UserCreationForm()
    return render_to_response("base_usersignup.html", {
        'form': form}, RequestContext(request))
