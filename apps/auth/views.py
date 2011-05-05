from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import login as django_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout

def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          redirect_authenticated=None,
          authentication_form=AuthenticationForm):
    print "========= In apps/auth/login ============"
    context=RequestContext(request)

    form = authentication_form(data=request.POST)
    
    if request.method == "POST":
        print "username: ",
        print form.data['username']
        try:
            user = User.objects.get(username=form.data['username'])

        except:            
            user = User.objects.get(username='') # needed to prevent using user.is_authenticated() NEED A BETTER WAY TO AVOID THIS!
            return django_login(request, template_name=template_name,
                                redirect_field_name=redirect_field_name,
                                authentication_form=authentication_form)
        
        if user.is_active == False:
            print "NOT ACTIVATED YET"
            user_name = user.username

            return render_to_response('base_login.html', 
                                      { 'form': form, 
                                        'username': user_name,
                                        'need_activation': True,
                                        },
                                      context_instance=RequestContext(request))
            


    return django_login(request, template_name=template_name,
                        redirect_field_name=redirect_field_name,
                        authentication_form=authentication_form)
