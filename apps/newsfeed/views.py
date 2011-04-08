# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

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
            
def newsfeed(request)
    errorMsg = None

    # check that the url corresponds to a valid group
    user = request.user
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
        errorMsg = handle_submit(group, request)
        if errorMsg:
            print errorMsg

    # handle a possible post deletion
    if 'delete_submit' in request.POST:
        handle_post_delete(request)

    children = group.child_set.all()
    posts = Filter().get_posts(group) # runs posts through an empty filter
    wall_filter_list = Filter.get_wall_filter_list(group.name);
    #annotate(score=hot('post__upvotes', 'post__downvotes', 'post__date')).order_by('score')
    return render_to_response('base_wall_group.html',
                              {'posts': posts,
                              'errormsg': errorMsg,
                              'group': group,
                              'children': children,
                              'filter_list': wall_filter_list,
                              'filter_view_url': '/_apps/wall/views-filter_wall/'},
                              context_instance=RequestContext(request))
