# Create your views here.

from OneTree.apps.common.models import *
from OneTree.apps.helpers.enums import PostType
from OneTree.apps.helpers.filter import Filter
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def group(request):
    pass

def update_vote(request):
    if request.is_ajax():
        post_id = request.GET.get("post_id")
        vote_type = request.GET.get("vote_type")
        post_type = int(request.GET.get("post_type"))
        if post_id and vote_type and post_type:
            if post_type == PostType.ANNOUNCEMENT:
                post = Announcement.objects.get(id=post_id)
            elif post_type == PostType.EVENT:
                post = Event.objects.get(id=post_id)
            else:
                post = None
            
            if post:
                if vote_type == 'up':
                    if post.upvotes == None:
                        post.upvotes = 1
                    else:
                        post.upvotes += 1
                else:
                    if post.downvotes == None:
                        post.downvotes = 1
                    else:
                        post.downvotes += 1
                post.save()
                return HttpResponse()
                #score = post.upvotes - post.downvotes;
                #return HttpResponse(score, mimetype="application/javascript")

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
            filters.parse_request(group, request);
            filtered_posts = filters.get_posts(group);
            return render_to_response('includes/wall/wall_content.html',
                                      {'posts':filtered_posts,
                                       'group': group,},
                                      context_instance=RequestContext(request))

    return HttpResponse(status=400)
