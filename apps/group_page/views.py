# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from OneTree.apps.common.models import *

'''
Is it ultimately going to be a pain when generating the wall that we
have separate models for announcements and events? Post has no objects
managers, so it's not simple to just query all posts. We may have to do
a merge of the event and announcements lists for display on the wall. Maybe
this would not be necessary if posts were not abstract?
'''

'''
Note: In common or something, we should keep all of these string
literals in a text.en file
'''

'''
Note: Even though I check for multiple groups mapping to the same url here
we should figure out how to enforce url uniqueness in our model.
'''

'''
Concatenate's group's announcements and events with that of its children
for percolation. Returns a tuple of the form (announcements, events),
where each element is the concatenated result.

Note that this only currently checks the first level of depth. I suppose
we may want to save this result in group.

We also may want to include timestamps to make this more efficient and/or
to limit database stress (ie: only update every 60 seconds).
'''
def concat_with_child_posts(group):
   announcements = group.announcement_set.all()
   events = group.event_set.all()

   # create one list of all announcements; i wonder if this is efficient
   children = group.child_set.all()
   postsPerChild = 5 # maximum number of each type of post to get from a child
   for child in children:
      child_announcements = child.announcement_set.all()[:postsPerChild]
      child_events = child.event_set.all()[:postsPerChild]      
      announcements = announcements | child_announcements;
      events = events | child_events;
   return (announcements, events)
   
def group_page(request, group_url):
   errormsg = None

   # check that the url corresponds to a valid group
   group = Group.objects.filter(url=group_url)
   if len(group) > 1:
      errormsg = "Database Error. URL mapped to multiple groups."
      return render_to_response('error_page.html', {'errormsg': errormsg,})
   elif len(group) == 0:
      errormsg = "Group doesn't exist."
      return render_to_response('error_page.html', {'errormsg': errormsg,})
   else:
      group = group[0] # only one element in queryset

   # get the data that was perhaps submitted
   if request.method == 'POST':
      if 'post_content' in request.POST and request.POST['post_content']:
          # later insert logic to distinguish events vs announcements
          new_announcement = Announcement(text=request.POST['post_content'],
                                          group=group)
          new_announcement.save()
      else:
          errormsg = "Empty announcement? Surely you aren't *that* boring."

   # now get the announcements and render them
   (announcements, events) = concat_with_child_posts(group)

   # is there a better way to do this group_url parameter???
   return render_to_response('base_wall_group.html',
                             {'announcements': announcements,
                             'errormsg': errormsg,
                             'group_name': group.name},
                             #'group_url': ('/group/' + group_url + '/')},
                             context_instance=RequestContext(request))
