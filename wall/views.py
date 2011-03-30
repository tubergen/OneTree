# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from OneTree.wall.models import *

'''
Is it ultimately going to be a pain when generating the wall that we
have separate models for announcements and events? Post has no objects
managers, so it's not simple to just query all posts. We may have to do
a merge of the event and announcements lists for display on the wall. Maybe
this would not be necessary if posts were not abstract?
'''

def group(request):
    errormsg = None
    if 'post_content' in request.POST and request.POST['post_content']:
        # later insert logic to distinguish events vs announcements
        new_announcement = Announcement(text=request.POST['post_content'])
        new_announcement.save()
    else:
        errormsg = "Empty announcement? Surely you aren't *that* boring."
    announcements = Announcement.objects.all()
    return render_to_response('group_page.html',
                              {'announcements': announcements,
                              'errormsg': errormsg,},
                              context_instance=RequestContext(request))
