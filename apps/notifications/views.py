# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from OneTree.apps.common.notification import *
from operator import attrgetter
from OneTree.apps.common.models import *
from OneTree.apps.newsfeed.views import get_most_recent_pics

from itertools import chain

@login_required
def answer_notif(request):
    err_loc = ' Error at submit_yes in notifications/views.py.'
    if request.method == 'POST':
        try:
            notif_id = int(request.POST.get('notif_id'))
        except ValueError:
            print 'notif_id not int.' + err_loc
            return HttpResponse(status=400)
        answer = request.POST.get('answer')
        
        if notif_id and answer:
            notif = Notification.objects.get(id=notif_id)
            if notif:
                if answer == 'yes':
                    notif.cast().handle_yes()
                elif answer == 'no':
                    notif.cast().handle_no()
                else:
                    print 'Answer not yes or no.' + err_loc
                    return HttpResponse(status=400)
                
                if request.is_ajax():
                    # notif was updated, so need to re-query
                    notif = Notification.objects.get(id=notif_id).cast()
                    return HttpResponse(notif.answer_descrip)                
                else:
                    return HttpResponseRedirect('/notifications/');
    return HttpResponse(status=400)

@login_required
def notification_page(request):
    profile = request.user.get_profile()

    ''' Ming: Why are you passing user and profile to the template
    in the context? You probably don't want to do this. Use
    {{ request.user }}, {{ request.user.get_profile }} in template. '''

### Ming's section #################
    errormsg = None
    need_approval = False

    groups = Group.objects.filter(admins=request.user)
        
    if groups:
        for group in groups:
            if group.inactive_child.all():
                need_approval = True
            else:
                pass 

##########################

    (pending_notifs, old_notifs) = profile.get_notifs();

    # set all new notifications to not new, since now we'll see them
    for notif in profile.get_new_notifs():
        notif.not_new()

    pending_notifs = sorted(pending_notifs, key=attrgetter('date'), reverse=True)
    old_notifs = sorted(old_notifs, key=attrgetter('date'), reverse=True)    

    max_old_notifs = 20
    if len(old_notifs) > max_old_notifs:
        old_notifs = old_notifs[0:max_old_notifs]

    new_pics = get_most_recent_pics(request.user);

    return render_to_response('newsfeed/base_newsfeed.html',
                             {'pending_notifs': pending_notifs,
                              'old_notifs': old_notifs,
                              'notif_view_url': '/_apps/notifications/views-answer_notif/',
                              'pictures': new_pics,                              
                              'userprofile': profile,
                              'need_approval': need_approval,
                              'active': request.user.is_active,
                              'is_notif_page': True,
},
                             RequestContext(request));    
