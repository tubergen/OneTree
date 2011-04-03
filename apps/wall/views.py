# Create your views here.

from OneTree.apps.common.models import *
from OneTree.apps.common.enums import PostType
from OneTree.apps.group_page.views import get_posts
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
                return HttpResponse();
                #score = post.upvotes - post.downvotes;
                #return HttpResponse(score, mimetype="application/javascript")

    return HttpResponse(status=400)

''' Instead of passing a single filter type string, perhaps pass in multiple
filters in a list, and add them to the dictionary incrementally?'''
def filter_wall(request):
    print "made it!!"
    if request.is_ajax():
        filter_type = request.GET.get("filter_type")
        if filter_type:
            print filter_type
            #if filter_type == 'this_group_only':
            #    posts = get_posts(request.group, {filter_type:request.group,})
            #else:
            print "here"
            #print request.get
            posts = get_posts(request.group, {})

            print "return"
            return render_to_response("/wall/wall_content.html",
                                      {'posts':filtered_posts,
                                       'errormsg': request.errormsg,
                                       'group': request.group,
                                       'children': request.children},
                                      context_instance=RequestContext(request))

    return HttpResponse(status=400)
