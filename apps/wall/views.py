# Create your views here.

from OneTree.apps.common.models import *
from OneTree.apps.helpers.enums import PostType, VoteType
from OneTree.apps.helpers.filter import Filter
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def post_comment(request):
    # security: sanitize input?
    post_id = int(request.POST.get("post_id"))
    redirect = request.POST.get("next")
    comment_text = request.POST.get("comment_text")
    post_type = int(request.POST.get("post_type"))
    this_level = 0; # change this when you add comments to comments
    if post_id and comment_text and post_type and request.user.is_authenticated():
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
            filters = Filter();
            filters.parse_request(request);
            filtered_posts = filters.get_posts(group);
            return render_to_response('includes/wall/wall_content.html',
                                      {'posts': filtered_posts,
                                       'group': group,},
                                      context_instance=RequestContext(request))

    print 'HTTP 400 returned in filter_wall()'    
    return HttpResponse(status=400)
