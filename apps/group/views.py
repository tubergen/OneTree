# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from OneTree.apps.common.models import *
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.enums import PostType
from OneTree.apps.group.helpers import *
from OneTree.apps.common.group import Group, GroupForm


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
            if 'eventclick' in request.POST and request.POST['eventclick']:
                errormsg = handle_event(group, request)
            else:
                errormsg = handle_ann(group, request)
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
    print 'in delete_post'

    err_loc = ' See delete_post in the group_page views.py.'
    if request.method == 'POST':
        # Get parameters
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
                    if request.user in group.admins.all():
                        post.delete()
#                    else:
#                        print "Not allowed to delete post"
                else:
                    manager.remove(post)

                return HttpResponse()
            
            except ObjectDoesNotExist:
                print 'Error: Tried to delete non-existent object.' + err_loc
                
    return HttpResponse(status=400)

#######################################
# GROUP PAGE
#######################################
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
    #    Note: I deliberately do not catch Profile.DoesNotExist here,
    #    since all logged in users should have a profile
    try:
        request.user.get_profile().subscriptions.get(id=group.id)
        user_is_subscribed = True
    except (Group.DoesNotExist, AttributeError): 
        # Note: attribute error occurs when user is AnonymousUser
        user_is_subscribed = False

    # get user's list of voted posts
    try:
        voted_post_set = request.user.get_profile().get_voted_posts(group)
    except (AttributeError):
        # Note: attribute error occurs when user is AnonymousUser
        voted_post_set = None

    children = group.child_set.all()
    posts = Filter().get_posts(group) # runs posts through an empty filter
    wall_filter_list = Filter.get_wall_filter_list(group.name);
    #annotate(score=hot('post__upvotes', 'post__downvotes', 'post__date')).order_by('score')

    groupadmins = group.admins.all()

    if request.user in groupadmins:
        is_admin = True
        submit_off = False
        print "submit on"
    else:
        is_admin = False
        submit_off = True
        print "submit off"


    return render_to_response('group/base_group.html',
                              {'posts': posts,
                               'is_admin': is_admin,
                               'submit_off': submit_off,
                              'errormsg': errormsg,
                              'group': group,
                              'children': children,
                              'user_is_subscribed': user_is_subscribed,
                              'subscribe_view_url':'/_apps/newsfeed/views-change_subscribe/',
                              'filter_list': wall_filter_list,
                              'filter_view_url': '/_apps/wall/views-filter_wall/',
                              'delete_post_view_url': '/_apps/group_page/views-delete_post/',
                               'voted_post_set': voted_post_set,},
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


# REFERENCES:
# http://docs.djangoproject.com/en/dev/topics/forms/modelforms/
#     the above one has info on changing existing objects
#     that should be useful later on when editing content.
# http://docs.djangoproject.com/en/dev/topics/forms/
# http://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound

def create_group(request):
    if not request.user.is_authenticated():
        return render_to_response("base_loginerror.html", RequestContext(request));
    if request.method == 'POST':        

        form = GroupForm(request.POST) # Form bound to POST data
        if form.is_valid():   # NEED TO ADD VALIDATION!

            # Save information of group to be registered
            new_group = form.save(commit=False)

            # Get parent group
            try:
                parent = Group.objects.get(name=new_group.parent)
                print 'parent is: ',
                print parent
            except:
                parent = None
                # is this really the best way to handle it =\

            # Create the group but prevent parent from being created
            new_group.parent = parent
            new_group.save()

            # Add parent to inactive parent list
            try: 
                group = Group.objects.get(url=new_group.url)
                print 'New group created: ',
                print group
                group.inactive_parent = parent
                group.save()
            except:
                pass      

            taglist = request.POST['keywords'].split()
            new_tags = []
            for tags in taglist:
                new_tag, created = Tag.objects.get_or_create(tag=tags)
                if created:
                    new_tag.save()
                new_tags.append(new_tag)

            new_group = form.save()
            for tag in new_tags:
                new_group.tags.add(tag)


            # there is probably a more elegant way to associate admin to a group
            currentgroup = Group.objects.get(name=form.cleaned_data['name'])
            currentgroup.addAdmin(request.user)
            currentgroup.save()
                                            
            #name = form.cleaned_data['name']
            #parent = form.cleaned_data['parent']
            #url = form.cleaned_data['url']

            # is this all? should we "clean the data"? what does
            # validation actually do?? it seems to work.
            return HttpResponseRedirect('/group/' + form.cleaned_data['url'])

        else:
            print 'wtf'
            return render_to_response('base_groupsignup.html', {'form': form,},
                    RequestContext(request)) # change redirect destination
    else:
        form = GroupForm() # An unbound form - can use this for error messages

    return render_to_response('base_groupsignup.html', {'form': form,}, RequestContext(request))
