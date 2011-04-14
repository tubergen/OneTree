from OneTree.apps.common.models import *
import string


# code for handling event
def handle_event(group, request):
    errormsg = None
    if not request.POST['title'] or not request.POST['where'] or not request.POST['date'] or not request.POST['time']:
        errormsg = 'Please fill out all required fields for an event.'
    
    else:
        title = request.POST['title'].strip()
        url = string.join(request.POST['title'].split(), '')
        url = url.strip()
        when = request.POST['date'] + ' '
        flaglist = request.POST['flags'].split(',')
        for x in range(0, len(flaglist)):
            flaglist[x] = flaglist[x].strip()
            new_flags = []
        for flag in flaglist:
            new_flag = Flag(name=flag)
            new_flag.save()
            new_flags.append(new_flag)
        # messy time code; perhaps move it somewhere else?
        time = request.POST['time'].split(':')
        if len(time) == 1:
            minutes = '00'
        else:
            minutes = time[1]
        if not time[0].isdigit() or not minutes.isdigit() or int(time[0]) < 1 or int(time[0]) > 12 or int(minutes) > 59:
            errormsg = 'Please enter a valid time'
            return errormsg
                        
        if request.POST['timedrop'] == 'am':
            if time[0] == '12':
                new_time = '00:' + minutes
            else:
                new_time = time[0] + ':' + minutes
        else:
            format_time = int(time[0])
            if format_time == 12:
                new_time = str(format_time) + ':' + minutes
            else:
                hour = format_time + 12
                new_time = str(hour) + ':' + minutes
        when += new_time
        # end messy time code
        new_event = Event(text=request.POST['post_content'],
                          upvotes = 0,
                          downvotes = 0,
                          origin_group=group,
                          event_title=title,
                          event_place=request.POST['where'],
                          event_date=when,
                          event_url=url)
        new_event.save()
        for flag in new_flags:
            new_event.flags.add(flag)
        group.events.add(new_event)
        group.addEventToParent(new_event)

    return errormsg


# code for handling announcement
def handle_ann(group, request):
    new_announcement = Announcement(text=request.POST['post_content'],
                                    upvotes = 0,
                                    downvotes = 0,
                                    origin_group=group)

    new_announcement.save()
    group.announcements.add(new_announcement)
    group.addAnnToParent(new_announcement)
    return None
