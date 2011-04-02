from OneTree.apps.user_signup.models import UserForm, DivErrorList
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

# REFERENCES:
# http://docs.djangoproject.com/en/dev/topics/forms/modelforms/
#     the above one has info on changing existing objects
#     that should be useful later on when editing content.
# http://docs.djangoproject.com/en/dev/topics/forms/
# http://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound

def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, error_class=DivErrorList) # Form bound to POST data
        if form.is_valid():    # Add validation
            form.save()

            #first_name = form.cleaned_data['first_name']
            #last_name = form.cleaned_data['last_name']
            #email = form.cleaned_data['url']

            # necessary?
            
            # where should this redirect to? user info page?
           # return HttpResponseRedirect('/user/' + form.cleaned_data['last_name'])

        else:
            return render_to_response('base_usersignup.html', {'form': form, 'is_first_attempt': False,}, RequestContext(request)) # change redirect destination

    else:
        form = UserForm(error_class=DivErrorList) # An unbound form - can use this for error messages
    return render_to_response('base_usersignup.html', {'form': form, 'is_first_attempt': True,}, RequestContext(request))
