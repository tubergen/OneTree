# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from OneTree.apps.common.models import *

import datetime

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
                                               origin_group=group)
            new_announcement.save()
            group.announcements.add(new_announcement)
            group.addAnnToParent(new_announcement)
        else:
            errormsg = "Empty announcement? Surely you aren't *that* boring."

    children = group.child_set.all()
    return render_to_response('base_wall_group.html',
                              {'announcements': group.announcements.all(),
                              'errormsg': errormsg,
                              'group': group,
                              'children': children},
                              context_instance=RequestContext(request))

'''
This was a function intended to do a dfs, having each parent node query
it's children and updating it's own announcement / event lists if
necessary. Then Jorge and I  realized that it's much easier to just push
announcements and events up on their creation.

Leaving this in here b/c it might be useful later for applications where
we do want parents to query their children.

However, note that this DOES NOT WORK at all right now. AT ALL.

marked = {} # keep track of all children reached in update tree dfs
timeBetweenQueries = 0 # change later if our site has heavy traffic
postsPerChild = 5 # maximum number of each type of post to get from a child

def update_tree(group):
    marked = {}
    dfs(group)

def dfs(group):
    marked[group.id] = True
    announcements = group.announcement_set.all()
    events = group.event_set.all()

    children = group.child_set.all()
    curTime = datetime.datetime.now()
    for child in children:
        if (not marked.get(child.id)): #and child.hasNewPosts and
        #        child.last_update_time.AddSeconds(timeBetweenQueries) < curTime):

            dfs(child)
            
            child_announcements = child.announcements.order_by('-date').values_list('id', flat=True)[:postsPerChild]
            group.announcements.add(child_announcements[0])
            
            child_events = child.events.order_by('-date').values_list('id', flat=True)[:postsPerChild]
            group.events.add(child_events)
            
            #announcements = announcements | child_announcements;
            #events = events | child_events;

            child.last_update_query = datetime.now()
            child.hasNewPosts = False
'''
