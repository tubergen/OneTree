# Create your views here.

from OneTree.apps.common.models import *
from OneTree.apps.helpers.enums import PostType, VoteType
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.paginate import paginate_posts
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def post_comment(request):
    default_comment_text = 'type comment here!'
    # security: sanitize input?
    post_id = int(request.POST.get("post_id"))
    redirect = request.POST.get("next")
    comment_text = request.POST.get("comment_text")
    post_type = int(request.POST.get("post_type"))
    this_level = 0; # change this when you add comments to comments
    if post_id and comment_text and post_type and request.user.is_authenticated() \
           and comment_text != default_comment_text:
        if post_type == PostType.ANNOUNCEMENT:
            post = Announcement.objects.get(id=post_id)
            new_comment = Comment(text = comment_text,
                    announcement = post, author = request.user,
                    level = this_level)
            new_comment.save()
        elif post_type == PostType.EVENT:
            post = Event.objects.get(id=post_id)
            new_comment = Comment(text = comment_text,
                    event = post, author = request.user,
                    level = this_level)
            new_comment.save()
        elif post_type == PostType.COMMENT:
            post = Comment.objects.get(id=post_id)
            print post_id

            # figure out how deep it is
            this_level = 1
            top_post = post
            if post:
                while int(top_post.level) != 0:
                    this_level += 1
                    top_post = top_post.parent_comment

                new_comment = Comment(text = comment_text,
                        parent_comment = post, author = request.user,
                        level = this_level)
                new_comment.save()
        else:
            # RETURN SOME ERROR MESSAGE DUDE
            pass

    return HttpResponseRedirect(redirect)

''' Who exactly can delete comments anyway? '''
removed_by_admin = 'This comment was removed by a page administrator.'
removed_by_user = 'This comment was removed by its author.'
def delete_comment(request):
    err_loc = ' See delete_comment in the group_page views.py.'
    if request.method == 'POST':
        try:
            comment_id = int(request.POST.get('comment_id'))
        except:
            print 'Comment id not valid integer.' + err_loc
            return HttpResponse(status=400)

        try:
            group_id = int(request.POST.get('group_id'))
            group = Group.objects.get(id=group_id)
        except:
            group = None

        if comment_id:
            try:
                comment = Comment.objects.get(id=comment_id)
            
                if request.user == comment.author:
                    comment.text = removed_by_user;
                    removed_msg = removed_by_user;
                elif group and request.user in group.admins.all():
                    comment.text = removed_by_admin;
                    removed_msg = removed_by_admin;
                else:
                    print 'User not allowed to remove comment.' + err_loc
                    return HttpResponse(status=400)
                
                comment.removed = True
                comment.save();
                return HttpResponse(removed_msg)
            except ObjectDoesNotExist:
                print 'Non-existent group or comment.' + err_loc
    return HttpResponse(status=400)

def group(request):
    pass

@login_required
def update_vote(request):
    if request.is_ajax() and request.method == 'POST':
        post_id = request.POST.get("post_id")
        vote_type = request.POST.get("vote_type")
        post_type = int(request.POST.get("post_type"))
        profile = request.user.get_profile()
        if post_id and vote_type and post_type and profile:
            if post_type == PostType.ANNOUNCEMENT:
                post = Announcement.objects.get(id=post_id)
            elif post_type == PostType.EVENT:
                post = Event.objects.get(id=post_id)
            else:
                post = None
            
            if post:
                if vote_type == 'up':
                    vt = VoteType.UP
                else:
                    vt = VoteType.DOWN

                (up_change, down_change) = profile.change_vote(post_id, post_type, vt)

                if up_change == None and down_change == None:
                    return HttpResponse(status=400) # there was an error

                post.update_vote(VoteType.UP, up_change)
                post.update_vote(VoteType.DOWN, down_change)
                change = up_change + down_change * -1; # lol math
                return HttpResponse(str(change))

    return HttpResponse(status=400)

'''
I wanted to submit a dictionary of filters to this function. However, I think
this may be hard / impossible. See:

http://stackoverflow.com/questions/3397217/jquery-submit-a-js-object-via-ajax-to-django-view
'''
def filter_wall(request):
    if request.is_ajax():
        group_id = request.GET.get("group_id")
        if group_id:
            group = Group.objects.get(id=group_id)
            start_date = request.GET.get("start_date") # defaults to None
            end_date = request.GET.get("end_date")  # defaults to None
            filters = Filter();
            filters.parse_request(request);
            filtered_posts = filters.get_posts(group, start_date, end_date);

            posts_on_page = paginate_posts(request, filtered_posts)

            if request.user.is_authenticated():
                is_admin = request.user.get_profile().is_admin_of(group)
            else:
                is_admin = False

            return render_to_response('includes/wall/wall_content.html',
                                      {'posts': posts_on_page.object_list,
                                       'posts_on_page': posts_on_page,
                                       'group': group,
                                       'is_admin': is_admin,
                                       'delete_post_view_url': '/_apps/wall/views-delete_post/',},
                                      context_instance=RequestContext(request))

    print 'HTTP 400 returned in filter_wall()'    
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
def delete_post(request):
    err_loc = ' See delete_post in the wall views.py.'
    if request.method == 'POST':
        try:
            group_id = int(request.POST.get('group_id'))
            post_id = int(request.POST.get('post_id'))
            post_type = int(request.POST.get('post_type'))
        except:
            print 'Wall post delete POST data were not valid integers.' + err_loc
            return HttpResponse(status=400)

        print 'here'
            
        if group_id and post_id and post_type:
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
