from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from OneTree.apps.user_signup.forms import RegistrationForm
from OneTree.apps.user_signup.models import RegistrationProfile


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

def oldregister(request):
    if request.method == 'POST':
        print request.POST
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/user/" + new_user.username)
    else:
        form = UserCreationForm()
    return render_to_response("base_usersignup.html", {
        'form': form}, RequestContext(request))

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]

            new_user = RegistrationProfile.objects.create_inactive_user(username, email, password)
            return render_to_response("registration_success.html",
                                      { 'username': username, 'email':email, 'password':password} 
                                      )
    else:
        form = RegistrationForm()
        

    context = RequestContext(request)

    return render_to_response("register.html",
                              {'form': form},
                              context_instance=context)



def verify_key(request, activation_key):
    """
    Given an an activation key, look up and activate the user
    account corresponding to that key (if possible).
    
    """
    activated = RegistrationProfile.objects.activate_user(activation_key)
    return activated





def activate(request, **kwargs):
    
    account = verify_key(request, **kwargs)

    if account:
        return redirect("reg_complete")

    context = RequestContext(request)

    return render_to_response("activate_n.html",
                              kwargs,
                              context_instance=context)


