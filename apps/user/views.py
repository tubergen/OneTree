from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from OneTree.apps.user.forms import RegistrationForm
from OneTree.apps.user.models import RegistrationProfile

from OneTree.apps.common.models import *
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

import datetime


def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            print new_user

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]

            user = authenticate(username=username, password=password)
            if user is None:
                print "Sorry"
            else:
                print "hey ",
                print login(request, user)

            print "login done"
            return render_to_response("base_user.html",
                                      { 'email': "secret signup email", 'password': "secret signup password"} 
                                      )
    else:
        form = UserCreationForm()
    return render_to_response("base_usersignup.html", {
        'form': form}, RequestContext(request))

def register(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]

            new_user = RegistrationProfile.objects.create_inactive_user(username, email, password)
            
            user = authenticate(username=username, password=password)
            if user is None:
                print "Sorry"
            else:
                login(request, user)

            return render_to_response("registration_success.html",
                                      { 'email':email, 'password':password },
                                      context_instance=context
                                      )
    else:
        form = RegistrationForm()



    return render_to_response("register.html",
                              {'form': form},
                              context_instance=context)

def activate(request, activation_key):
    context = RequestContext(request)
    
    # First, validate activation key
    try:
        profile = RegistrationProfile.objects.get(activation_key=activation_key)
        print "PROFILE: ",
        print profile

    # If activation key is not found
    except:
        print "Bad activation key"
        return render_to_response("activate_n.html",
                                  activation_key,
                                  context_instance=context)
    
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            account = verify_key(request, activation_key)
            
            if account:
                login(request, user)
                return redirect("reg_complete", context_instance=context)
        else:
            pass


    return render_to_response("act.html", 
                              { 'activation_key': activation_key, },
                              context_instance=context
                              )




def verify_key(request, activation_key):
    """
    Given an an activation key, look up and activate the user
    account corresponding to that key (if possible).
    
    """
    activated = RegistrationProfile.objects.activate_user(activation_key)
    return activated


@login_required
def user_page(request, username):
    print "In user_page"
    errormsg = None

    if not username: # no username means they're trying to view their own profile
        if request.user.is_authenticated():
            user = request.user
            
            try: # may not need try because filter seems to return empty set when no result is found
                groups = Group.objects.filter(admins=user)

                if groups:
                    for group in groups:
                        if group.inactive_parent is not None:
                            print "Group with inactive parent:",
                            print group.name
                else:
                    print "No groups found"
            except:
                print "No groups detected"
                
            return render_to_response('base_user.html',
                                      {'user': user, 
                                       'groups': groups, 
                                       'active': user.is_active },
                                      context_instance=RequestContext(request))        


        else:
            return render_to_response('base_loginerror.html', 
                    context_instance=RequestContext(request));


        # I don't think we need this else?
    else:
        # check that the url corresponds to a valid user
        user = User.objects.filter(username=username)
        if len(user) > 1:
            errormsg = "Database Error. URL mapped to multiple users."
            return render_to_response('error_page.html', {'errormsg': errormsg, })
        elif len(user) == 0:
            errormsg = "User %s doesn't exist" % username # SHOULD CLEAN THIS?
            return render_to_response('error_page.html', {'errormsg': errormsg, })
        else:
            user = user[0] # only one element in query


    return render_to_response('base_user.html',
                              {'user': user, },
                              context_instance=RequestContext(request))

def user_account(request, username):
    if not username:
        print "cool"
    else:
        print "ok"
