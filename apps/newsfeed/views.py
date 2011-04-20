# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse  

from OneTree.apps.common.models import *
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.enums import PostType

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

'''
Looks at request. If request specifies a post should be deleted / remmoved, then
it's deleted if the requester is the administrator of the author group; if not,
then the post is simply removed from the group's page. 

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

    if not posts:
        errormsg = "No news. Join some more communities !"
    
    newsfeed_filter_list = Filter.get_newsfeed_filter_list();

    voted_post_set = request.user.get_profile().get_voted_posts();

    # for debugging
    print request.user

    return render_to_response('newsfeed/base_newsfeed.html',
                              {'posts': posts,
                              'errormsg': errormsg,
                              'submit_off': True,
                              'voted_post_set': voted_post_set,
                              'filter_list': newsfeed_filter_list,
                              'filter_view_url': '/_apps/newsfeed/views-filter_newsfeed/',
                              'delete_post_view_url': '/_apps/newsfeed/views-remove_post/',},
                              context_instance=RequestContext(request))

    #return render_to_response('base_newsfeed.html');
