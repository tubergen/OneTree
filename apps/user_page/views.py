# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from OneTree.apps.common.models import *
from django.contrib.auth.models import User

import datetime

def user_page(request, username):
    errormsg = None

    if not username: # no username means they're trying to view their own profile
        if request.user.is_authenticated():
            user = request.user
        else:
            return render_to_response('base_loginerror.html', 
                    context_instance=RequestContext(request));
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
                              {'user': user},
                              context_instance=RequestContext(request))
