# Create your views here.

from OneTree.apps.common.models import *
from django.http import HttpResponse
from django.core import serializers

def group(request):
    pass

def update_vote(request):
    if request.is_ajax():
        ann_id = request.GET.get("ann_id")
        vote_type = request.GET.get("vote_type")
        if ann_id and vote_type:
            ann = Announcement.objects.get(id=ann_id)
            if ann:
                if vote_type == 'up':
                    if ann.upvotes == None:
                        ann.upvotes = 1
                    else:
                        ann.upvotes += 1
                else:
                    if ann.downvotes == None:
                        ann.downvotes = 1
                    else:
                        ann.downvotes += 1
                ann.save()
                score = ann.upvotes - ann.downvotes;
                return HttpResponse(score, mimetype="application/javascript")

    return HttpResponse(status=400)
