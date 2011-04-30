from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from OneTree.apps.common.models import Group

def homepage(request):
    toplevelgroups = Group.objects.filter(parent=None)
    return render_to_response("base_homepage.html", {'toplevelgroups': toplevelgroups}, RequestContext(request));
