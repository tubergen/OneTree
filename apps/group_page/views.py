# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from OneTree.apps.common.models import *
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.enums import PostType

import datetime
import string

'''
Note: In common or something, we should keep all of these string
literals in a text.en file
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
                if not request.POST['title'] or not request.POST['where'] or not request.POST['date'] or not request.POST['time']:
                    errormsg = 'Please fill out all required fields for an event.'
    
                else:
                    title = request.POST['title'].strip()
                    url = string.join(request.POST['title'].split(), '')
                    url = url.strip()
                    when = request.POST['date'] + ' '
                    flaglist = request.POST['flags'].split(',')
                    for x in range(0, len(flaglist)):
                        flaglist[x] = flaglist[x].strip()
                    new_flags = []
                    for flag in flaglist:
                        new_flag = Flag(name=flag)
                        new_flag.save()
                        new_flags.append(new_flag)
                    # messy time code; perhaps move it somewhere else?
                    time = request.POST['time'].split(':')
                    if len(time) == 1:
                        minutes = '00'
                    else:
                        minutes = time[1]
                    if not time[0].isdigit() or not minutes.isdigit() or int(time[0]) < 1 or int(time[0]) > 12 or int(minutes) > 59:
                        errormsg = 'Please enter a valid time'
                        return errormsg
                        
                    if request.POST['timedrop'] == 'am':
                        if time[0] == '12':
                            new_time = '00:' + minutes
                        else:
                            new_time = time[0] + ':' + minutes
                    else:
                        format_time = int(time[0])
                        if format_time == 12:
                            new_time = str(format_time) + ':' + minutes
                        else:
                            hour = format_time + 12
                            new_time = str(hour) + ':' + minutes
                    when += new_time
                    # end messy time code
                    new_event = Event(text=request.POST['post_content'],
                                      upvotes = 0,
                                      downvotes = 0,
                                      origin_group=group,
                                      event_title=title,
                                      event_place=request.POST['where'],
                                      event_date=when,
                                      event_url=url)
                    new_event.save()
                    for flag in new_flags:
                        new_event.flags.add(flag)
                    group.events.add(new_event)
                    group.addEventToParent(new_event)
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
Looks at request. If request specifies a post should be deleted / remmoved, then
it's deleted if the requester is the administrator of the author group; if not,
then the post is simply removed from the group's page. 

Don't forget to add authentication to this. Some permissions should be required
to be able to delete a post. 

I realize generally you make server-side changes with POST, not GET. However,
I see no reason to give the user a browser warning about "resubmission" here,
as would be the case with POST.

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
def delete_post(request):
    err_loc = ' See delete_post in the group_page views.py.'
    if request.method == 'POST':
        try:
            group_id = int(request.POST.get('group_id'))
            post_id = int(request.POST.get('post_id'))
            post_type = int(request.POST.get('post_type'))
        except:
            print 'Wall post delete POST data were not valid integers.' + err_loc
            return HttpResponse(status=400)
            
        if group_id and post_id and post_type:
            group_id = int(group_id)
            group = Group.objects.get(id=group_id)
            try: 
                if post_type == PostType.EVENT:
                    manager = group.events
                elif post_type == PostType.ANNOUNCEMENT:
                    manager = group.announcements                
                else:
                    print 'Tried to delete non-announcement non-event.' + err_loc
                    return HttpResponse(status=400)

                post = manager.get(id=post_id)
                if post.origin_group.id == group_id:
                    post.delete()
                else:
                    manager.remove(post)

                return HttpResponse()
            
            except ObjectDoesNotExist:
                print 'Error: Tried to delete non-existent object.' + err_loc
                
    return HttpResponse(status=400)
            
def group_page(request, group_url):
    errormsg = None

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
    if 'post_submit' in request.POST:
        errormsg = handle_submit(group, request)
        if errormsg:
            print errormsg

    # get user's subscription status to this group
    try:
        request.user.get_profile().subscriptions.get(id=group.id)
        user_is_subscribed = True
    except (Group.DoesNotExist, AttributeError): 
        # Note: attribute error occurs when user is AnonymousUser
        user_is_subscribed = False

    children = group.child_set.all()
    posts = Filter().get_posts(group) # runs posts through an empty filter
    wall_filter_list = Filter.get_wall_filter_list(group.name);
    #annotate(score=hot('post__upvotes', 'post__downvotes', 'post__date')).order_by('score')
    return render_to_response('group/base_group.html',
                              {'posts': posts,
                              'errormsg': errormsg,
                              'group': group,
                              'children': children,
                              'user_is_subscribed': user_is_subscribed,
                              'subscribe_view_url':'/_apps/newsfeed/views-change_subscribe/',
                              'filter_list': wall_filter_list,
                              'filter_view_url': '/_apps/wall/views-filter_wall/',
                              'delete_post_view_url': '/_apps/group_page/views-delete_post/',},                              
                              context_instance=RequestContext(request))

def event_page(request, groupname, title):
    errormsg = None
    
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
                              {'errormsg': errormsg,
                               'event': this_event},
                              context_instance=RequestContext(request))
