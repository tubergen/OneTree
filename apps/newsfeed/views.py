# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from OneTree.apps.common.models import *
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.enums import PostType
from django.http import HttpResponse  

@login_required
def filter_newsfeed(request):
    if request.is_ajax():
        user = request.user;
        if user:
            filters = Filter();
            filters.parse_request(None, request)
            filtered_posts = filters.get_news(user)
            return render_to_response('includes/wall/wall_content.html',
                                     {'posts': filtered_posts,},
                                     context_instance=RequestContext(request))

    print 'HTTP 400 returned in filter_newsfeed()'
    return HttpResponse(status=400)

@login_required
def change_subscribe(request):
    if request.is_ajax():
        user = request.user;
        group_id = request.GET.get("group_id")
        if group_id and user:
            manager = user.get_profile().subscriptions;
            
            # check to see if user is already subscribed
            try:
                subscribed_group = manager.get(id=group_id)
            except Group.DoesNotExist:
                subscribed_group = None

            group = Group.objects.get(id=group_id)
            if subscribed_group == None: # then subscribe the user
                manager.add(group)
            else:                 # then unsubscribe the user
                manager.remove(group)
        else:
            return HttpResponse(status=400)
    return HttpResponse()

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
@login_required
def handle_post_delete(request):
    err_loc = ' See handle_post_delete in the newsfeed views.py.'
    if request.method == 'POST':
        try:
            profile = request.user.get_profile()
        except AttributeError:
            print 'Error: User is either None or Anonymous'
            return
        try:
            post_id = int(request.POST.get('post_id'))
            post_type = int(request.POST.get('post_type'))
        except:
            print 'Error: Wall post delete POST data were not integers.' + err_loc
            return
        
        if profile and post_id and post_type:
            try: 
                if post_type == PostType.EVENT:
                    post = Event.objects.get(id=post_id)
                    profile.deleted_events.add(post)
                elif post_type == PostType.ANNOUNCEMENT:
                    post = Announcement.objects.get(id=post_id)
                    profile.deleted_anns.add(post)                    
                else:
                    print 'Tried to delete non-announcement non-event.' + err_loc
            except ObjectDoesNotExist:
                print 'Error: Tried to delete non-existent object.' + err_loc

@login_required
def newsfeed(request):
    errormsg = None

    # handle a possible post deletion
    if 'delete_submit' in request.POST:
        handle_post_delete(request)

    posts = Filter().get_news(request.user) # runs posts through an empty filter

    if not posts:
        errormsg = "No news. Join some more communities !"
    
    newsfeed_filter_list = Filter.get_newsfeed_filter_list();

    return render_to_response('newsfeed/base_newsfeed.html',
                              {'posts': posts,
                              'errormsg': errormsg,
                              'submit_off': True,
                              'filter_list': newsfeed_filter_list,
                              'filter_view_url': '/_apps/newsfeed/views-filter_newsfeed/'},
                              context_instance=RequestContext(request))

    #return render_to_response('base_newsfeed.html');
