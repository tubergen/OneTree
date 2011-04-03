# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from OneTree.apps.common.models import *

import datetime




def user_page(request, user_username):
    errormsg = None

    # check that the url corresponds to a valid user
    user = User.objects.filter(username=user_username)
    if len(user) > 1:
        errormsg = "Database Error. URL mapped to multiple users."
        return render_to_response('error_page.html', {'errormsg': errormsg, })
    elif len(user) == 0:
        errormsg = "User doesn't exist."
        return render_to_response('error_page.html', {'errormsg': errormsg, })
    else:
        user = user[0] # only one element in query

    # what does a user page contain? subscriptions from other groups?
    # for now, we'll just display the user's info

    #if request.method == 'POST':

    return render_to_response('base_user.html',
                              {'user': user},
                              context_instance=RequestContext(request))
        


