from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from OneTree.apps.user.forms import RegistrationForm, ActivationForm, EmailChangeForm

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
            return render_to_response("user/base_user.html",
                                      { 'email': "secret signup email", 
                                        'password': "secret signup password"} 
                                      )
    else:
        form = UserCreationForm()
    return render_to_response("base_usersignup.html", {
        'form': form}, RequestContext(request))

def register(request):
    context = RequestContext(request)

    # authenticated user should not be able to register 
    if request.user.is_authenticated():
	print "authenticated user"

	return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]

            new_user = RegistrationProfile.objects.create_inactive_user(username, email, password)

            """
            user = authenticate(username=username, password=password)
            if user is None:
                print "Sorry"
            else:
                login(request, user)
            """

            return render_to_response("registration_success.html",
                                      { 'username': username,
                                        'email':email, 'password':password },
                                      context_instance=context
                                      )
    else:
        form = RegistrationForm()



    return render_to_response("register.html",
                              {'form': form},
                              context_instance=context)

def activate(request, activation_key):
    # ADD: need to check if activation key has expired
    context = RequestContext(request)
    form = ActivationForm()
    error_msg = False

    # First, validate activation key
    try:
        profile = RegistrationProfile.objects.get(activation_key=activation_key)

    # If activation key is not found
    except:
        print "Bad activation key"
        return render_to_response("activate_n.html",
                                  activation_key,
                                  context_instance=context)
    
    if request.method == 'POST':
        form = ActivationForm(request.POST)

        # If username and password are valid (i.e. valid account)
        if form.is_valid(): 
            username = request.POST['username']
            password = request.POST['password']

            # If activation and account do not match
            if profile.user.username == username:

                # Get the user 
                # (actual authentication has been done in ActivationForm)
                user = authenticate(username=username, password=password)

                # Activate!
                user.is_active = True
                user.save()
                
                login(request, user)
                return render_to_response("reg_complete.html", 
                                          context_instance=context)

            else:
                error_msg = "The activation key does not correspond to your account."

    return render_to_response("act.html", 
                              { 'activation_key': activation_key, 
                                'form': form,
                                'error_msg': error_msg,
                                },
                              context_instance=context
                              )

@login_required
def user_page(request, username):
    print "In user_page"
    errormsg = None
    need_approval = False

    user = request.user
    userprofile = UserProfile.objects.get(user=request.user)
    groups = Group.objects.filter(admins=user)
        
    if groups:
        for group in groups:
            if group.inactive_child.all():
                need_approval = True
            else:
                pass 

    return render_to_response('user/base_user.html',
                              {'user': user, 
                               'userprofile': userprofile,
                               'groups': groups, 
                               'need_approval': need_approval,
                               'active': user.is_active, },
                              context_instance=RequestContext(request))    

@login_required
def user_account(request, username):
    context=RequestContext(request)

    return render_to_response('user/account.html',
                              { 'user': request.user },
                              context_instance=context
                              )

@login_required
def complete_profile(request):
    context=RequestContext(request)


    userprofile = UserProfile.objects.get(user=request.user)    
    print "USER >>>>>>>>>>"
    


    print "USER PROFILE >>>>>>>>>"
    print userprofile.user.first_name


    

    return render_to_response('user/complete_profile.html',
                              {

                              },
                              context_instance=context
                              )

    
@login_required
def admin_approve(request):
    context=RequestContext(request)

    need_approval = False

    user = request.user
    groups = Group.objects.filter(admins=user)

    # FOR DEBUGGING ############
    if groups:
        print "Group(s) with children awaiting approval:"
        for group in groups:
            if group.inactive_child is not None:
                print group.name,
                print ": ",
                print group.inactive_child.all()
        print ""
    else:
        print "No groups found"

    print "In admin_approve -- groups",
    print groups
    ############################


    if groups:
        for group in groups:
            if group.inactive_child.all():
                need_approval = True
            else:
                pass 


    if request.method == 'POST':
        data = request.POST

        print ">>>>>>>>>>>"


        user = request.user
        groups = Group.objects.filter(admins=user)
       
        for group in groups:
            for child in data.getlist(group.name):
                childgroup = Group.objects.get(name=child)
                group.inactive_child.remove(childgroup)

                childgroup.parent = group
                group.save()
                childgroup.save()
                print "SAVED"
                
    return render_to_response('user/base_approve.html',
                              { 'groups': groups, 
                                'need_approval': need_approval,
                                },
                              context_instance=context
                              )

@login_required
def change_email(request):
    context=RequestContext(request)

    u = request.user

    if request.method == 'POST':
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(username=u)
            print "here:"
            print user
            print ">"
            print user.email
 
    else:
        form = EmailChangeForm()

    return render_to_response('user/change_email.html',
                              { 'form': form },
                              context_instance=context
                              )

def password_change_success(request):
    context = RequestContext(request)
    
    return render_to_response('user/change_password_success.html',
                              {},
                              context_instance = context
                              )
    
def forget_password_email_sent(request):
    context = RequestContext(request)
    
    return render_to_response('user/forget_password_email_sent.html', 
                              {},
                              context_instance = context
                              )
    
