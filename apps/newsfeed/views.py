# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from OneTree.apps.common.models import *
from OneTree.apps.helpers.Filter import Filter
from OneTree.apps.helpers.enums import PostType

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
                if post_type == PostType.EVENT:
                    manager = group.events
                elif post_type == PostType.ANNOUNCEMENT:
                    manager = group.announcements                
                else:
                    print 'Tried to delete non-announcement non-event.' + err_loc
                    return

                post = manager.get(id=post_id)
                if post.origin_group.id == group_id:
                    post.delete()
                else:
                    manager.remove(post)
            
            except ObjectDoesNotExist:
                print 'Tried to delete non-existent object.' + err_loc

@login_required
def newsfeed(request):
    errorMsg = None

    user = request.user;
    profile = user.get_profile();
    subscriptions = profile.subscriptions;

    posts = Filter().get_posts(group) # runs posts through an empty filter

    if len(posts) < 1:
        errormsg = "You aren't part of any communities? That's sad. =("
    
    newsfeed_filter_list = Filter.get_newsfeed_filter_list();

    # handle a possible post deletion
    #if 'delete_submit' in request.POST:
    #    handle_post_delete(request)

    #annotate(score=hot('post__upvotes', 'post__downvotes', 'post__date')).order_by('score')
    return render_to_response('base_newsfeed.html',
                              {'posts': posts,
                              'errormsg': errorMsg,
                              'filter_list': newsfeed_filter_list,
                              'filter_view_url': '/_apps/wall/views-filter_wall/'},
                              context_instance=RequestContext(request))

    #return render_to_response('base_newsfeed.html');
