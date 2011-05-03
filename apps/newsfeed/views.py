# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse  

from OneTree.apps.common.models import *
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.enums import PostType

from heapq import heappushpop, heappush

@login_required
def filter_newsfeed(request):
    if request.is_ajax():
        user = request.user;
        if user:
            start_date = request.GET.get("start_date") # defaults to None
            end_date = request.GET.get("end_date")  # defaults to None
            filters = Filter()
            filters.parse_request(request)
            filtered_posts = filters.get_news(user, start_date, end_date);
            return render_to_response('includes/wall/wall_content.html',
                                     {'posts': filtered_posts,
                                      'is_newsfeed': True,
                                      'delete_post_view_url': '/_apps/newsfeed/views-remove_post/',},
                                     context_instance=RequestContext(request))

    print 'HTTP 400 returned in filter_newsfeed()'
    return HttpResponse(status=400)

'''
Looks at request. If request specifies a post should be deleted / removed, then
it's deleted if the requester is the administrator of the author group; if not,
then the post is simply removed from the group's page. 

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
def remove_post(request):
    err_loc = ' See remove_post in the newsfeed views.py.'
    if request.method == 'POST':
        # validate data
        try:
            profile = request.user.get_profile()
        except AttributeError:
            print 'Error: User is either None or Anonymous'
            return HttpResponse(status=400)

        try:
            post_id = int(request.POST.get('post_id'))
            post_type = int(request.POST.get('post_type'))
        except:
            print 'Error: Wall post delete POST data were not integers.' + err_loc
            return HttpResponse(status=400)
        
        if profile and post_id and post_type:
            if profile.remove_post(post_id, post_type): 
                return HttpResponse() # upon successful remove
            
    return HttpResponse(status=400)

@login_required
def newsfeed(request):
    errormsg = None

    posts = Filter().get_news(request.user) # runs posts through an empty filter

    wall_subtitle = ""
    if not posts:
        wall_subtitle = "No news. Join some more communities !"
    
    newsfeed_filter_list = Filter.get_newsfeed_filter_list();

    voted_post_set = request.user.get_profile().get_voted_posts();

    new_pics = get_most_recent_pics(request.user);

    # get one picture from each of your subscribed groups, then pick the four
    # most recent ones
    #pictures = Pictures.objects
    #.filter(created_date__lte=Y.created_date)
    
    return render_to_response('newsfeed/base_newsfeed.html',
                              {'posts': posts,
                              'pictures': new_pics,
                              'wall_subtitle': wall_subtitle,
                              'submit_off': True,
                              'is_newsfeed': True,
                              'voted_post_set': voted_post_set,
                              'filter_list': newsfeed_filter_list,
                              'filter_view_url': '/_apps/newsfeed/views-filter_newsfeed/',
                              'delete_post_view_url': '/_apps/newsfeed/views-remove_post/',},
                              context_instance=RequestContext(request))

    #return render_to_response('base_newsfeed.html');

''' return the num_pics most recent pics from user's subscribed groups ''' 
def get_most_recent_pics(user):
    subscriptions = user.get_profile().subscriptions.all();
    num_pics = 3
    num_stored = 0 # number of pictures added to most_recent_pics so far
    most_recent_pics = []
    for group in subscriptions:
        pictures = group.pictures.order_by('-upload_date')[0:num_pics]
        
        for p in pictures:
            if num_stored != num_pics:
                heappush(most_recent_pics, (p.upload_date, p))
                num_stored += 1
            elif most_recent_pics:
                (upload_date, image) = most_recent_pics[0]
                if upload_date < p.upload_date:
                    heappushpop(most_recent_pics, (p.upload_date, p))
            else: # not reached i think
                pass

    # now extract the actual pictures
    new_pics = []
    for date_pic_tuple in most_recent_pics:
        new_pics.append(date_pic_tuple[1])
    new_pics.reverse() # want most recent to least

    return new_pics
