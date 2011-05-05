from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from OneTree.apps.common.models import Group

def homepage(request):
    user_agent = request.META['HTTP_USER_AGENT']

    toplevelgroups = Group.objects.filter(toplevelgroup=True)
    # ^ this code si replicated in activate()

    # Check browser compatibility... this is a really simple check
    # To really ensure compatibility, we have to do version check too,
    # but I think this is sufficient for 333
    if ('Chrome' or 'Firefox') in user_agent:
	print "Compatible browser detected"
        compatible_browser = True
    else:
    	print "WARNING: INCOMPATIBLE BROWSER"
	compatible_browser = False

    return render_to_response("base_homepage.html", {'toplevelgroups': toplevelgroups, 'compatible_browser': compatible_browser}, RequestContext(request));
