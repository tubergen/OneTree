# Create your views here.

from OneTree.apps.common.models import *
from OneTree.apps.common.enums import PostType
from django.http import HttpResponse
from django.core import serializers

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
                score = post.upvotes - post.downvotes;
                return HttpResponse(score, mimetype="application/javascript")

    return HttpResponse(status=400)
