# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from OneTree.apps.common.models import *
from OneTree.apps.helpers.Filter import Filter
from OneTree.apps.helpers.enums import PostType

import datetime
import string

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
Looks at the wall post that was potentially submitted and, if any data was
submitted, adds that data to the database. Returns an errorMsg if there was a
error, which can be rendered. Returns None otherwise.
'''
def handle_submit(group, request):
    errormsg = None
    if request.method == 'POST':
        if 'post_content' in request.POST and request.POST['post_content']:

            # later insert logic to distinguish events vs announcement
            # this is probably not good logic
            if 'eventclick' in request.POST and request.POST['eventclick']:
                if not request.POST['title'] or not request.POST['where'] or not request.POST['when']:
                    errormsg = 'Please fill out all required fields for an event.'
                    pass                    

                else:
                    title = request.POST['title'].strip()
                    url = string.join(request.POST['title'].split(), '')
                    url = url.strip()
                    new_event = Event(text=request.POST['post_content'],
                                      upvotes = 0,
                                      downvotes = 0,
                                      origin_group=group,
                                      event_title=title,
                                      event_place=request.POST['where'],
                                      event_date=request.POST['when'],
                                      event_url=url)
                    new_event.save()
                    group.events.add(new_event)
                    group.addEventToParent(new_event)

                    if (request.POST['title'] == ''):
                        print "empty string"
                    elif (request.POST['title'] == None):
                        print "none"
                    else:
                        pass

                    if (new_event.event_title == ''):
                        print "title is empty"
            else:
                new_announcement = Announcement(text=request.POST['post_content'],
                                                upvotes = 0,
                                                downvotes = 0,
                                                origin_group=group)

                new_announcement.save()
                group.announcements.add(new_announcement)
                group.addAnnToParent(new_announcement)
        else:
            errormsg = "Empty post? Surely you aren't *that* boring."
    return errormsg

'''
Looks at request. If request specifies a post should be deleted (ie: removed),
then it's removed. Otherwise does nothing.

Don't forget to add authentication to this. Some permissions should be required
to be able to delete a post. 

SPECIAL NOTE : if there's ever a bug where an event mysteriously appears on the
wall only when "[this page]'s Posts Only" is selected, and it cannot be deleted,
it might be because of the line "post = manager.get(id=post_id)". If somehow a
post managed to get deleted from its creater's wall without it being deleted
completely from the database, then this behavior will occur. I think this is
impossible now, but I'm not 100% sure.

We could patch this up by instead getting the post with Event.objects.get(id=...)
etc. for each type of post. However, I am not doing this right now because it
would hide a bigger issue: that posts which are deleted on the creater's wall
are not completely deleted from the database.
'''
def handle_post_delete(request):
    err_loc = ' See handle_post_delete in the group_page views.py.'
    if request.method == 'POST':
        try:
            group_id = int(request.POST.get('group_id'))
            post_id = int(request.POST.get('post_id'))
            post_type = int(request.POST.get('post_type'))
        except:
            print 'Wall post delete POST data were not valid integers.' + err_loc
            return;
        if group_id and post_id and post_type:
            group_id = int(group_id)
            group = Group.objects.get(id=group_id)
            try: 
                if (post_type == PostType.EVENT):
                    manager = group.events
                elif (post_type == PostType.ANNOUNCEMENT):
                    manager = group.announcements                
                else:
                    print 'Tried to delete non-announcement non-event.' + err_loc
                    return

                post = manager.get(id=post_id)
                print post.origin_group.id
                print group_id
                if (post.origin_group.id == group_id):
                    post.delete()
                else:
                    manager.remove(post)
            
            except ObjectDoesNotExist:
                print 'Tried to delete non-existent object.' + err_loc
            
def group_page(request, group_url):
    errorMsg = None

    # check that the url corresponds to a valid group
    group = Group.objects.filter(url=group_url)
    if len(group) > 1:
        errormsg = 'Database Error. URL mapped to multiple groups.'
        return render_to_response('error_page.html', {'errormsg': errormsg,})
    elif len(group) == 0:
        errormsg = "Group doesn't exist."
        return render_to_response('error_page.html', {'errormsg': errormsg,})
    else:
        group = group[0] # only one element in queryset

    # handle the wall post that was perhaps submitted
    errorMsg = handle_submit(group, request)
    print errorMsg

    # handle a possible post deletion
    handle_post_delete(request)

    children = group.child_set.all()
    posts = Filter().get_posts(group) # runs posts through an empty filter
    #annotate(score=hot('post__upvotes', 'post__downvotes', 'post__date')).order_by('score')
    return render_to_response('base_wall_group.html',
                              {'posts': posts,
                              'errormsg': errorMsg,
                              'group': group,
                              'children': children},
                              context_instance=RequestContext(request))

def event_page(request, groupname, title):
    errorMsg = None
    
    # check that the url corresponds to a valid event
    this_event = Event.objects.filter(event_url=title)
    group = Group.objects.filter(event = this_event)
    if len(this_event) > 1:
        errormsg = 'Database Error. URL mapped to multiple events.'
        return render_to_response('error_page.html', {'errormsg': errormsg,})
    elif len(this_event) == 0:
        errormsg = "Event doesn't exist."
        return render_to_response('error_page.html', {'errormsg': errormsg,})
    else:
        this_event = this_event[0] # only one element in queryset
    return render_to_response('base_event.html',
                              {'errormsg': errorMsg,
                               'event': this_event},
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
