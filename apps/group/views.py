# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from OneTree.apps.common.models import *
from OneTree.apps.common.notification import *
from OneTree.apps.helpers.filter import Filter
from OneTree.apps.helpers.enums import PostType
from OneTree.apps.helpers.paginate import paginate_posts
from OneTree.apps.group.helpers import *
from OneTree.apps.common.group import Group, GroupForm

from django import forms
from django.db import models

from django.contrib.auth.decorators import login_required
import datetime
import string
import os
from PIL import Image

'''
Note: In common or something, we should keep all of these string
literals in a text.en file
'''

@login_required
def change_subscribe(request):
    if request.method == 'POST':
        profile = request.user.get_profile();
        group_id = request.POST.get("group_id")
        if group_id and profile:
            profile.change_subscribe(group_id)
            if request.is_ajax():
                return HttpResponse()
            else:
                group = Group.objects.get(id=group_id);
                return HttpResponseRedirect('/group/' +  group.url);
            
    return HttpResponse(status=400)

@login_required
def req_membership(request):
    print "========REQ_MEMBERSHIP====================="
    if request.method == 'POST':
        # Obtain group_id
        try:
            group_id = int(request.POST.get('group_id'))
        except TypeError:
            print 'group_id not int.' + err_loc
            print "=========================="
            return HttpResponse(status=400)
        if group_id:
            # Get the group that corresponds to the group_id
            group = Group.objects.get(id=group_id)
            print 'STATUS: getting group > ',
            print group
            # Check if there already exist a pending membership request
            pending_mem_req = MembershipReq.objects.filter(sender=request.user,
                                                           recv_group=group,
                                                           pending=True)
            
            print 'STATUS: pending_mem_req > ',
            print pending_mem_req


            # If there is no pending membership request, perform a request
            if not pending_mem_req:
                mem_req = MembershipReq(sender=request.user, recv_group=group)
                print "STATUS: mem_req > ",
                print mem_req
                mem_req.save()
            else: # Otherwise, do not do anything
                print 'Already a pending membership request.'

            # If request is ajax, ??
            if request.is_ajax():
                print "======================"
                return HttpResponse()
            else:
                print "======================="
                return HttpResponseRedirect('/group/' +  group.url);
    print "=============================="
    return HttpResponse(status=400)        

# Function to notify parent group that a child requests for approval
@login_required
def req_parent(request, pending_parent_name, requesting_child):
    # Parameters to be passed in:
    # - pending_parent_name (name of parent group)
    # - requesting_child (child group that makes the request)

    # Obtain group object corresponding to pending_parent
    
    print "=========REQ_PARENT==============="

    try:
        pending_parent = Group.objects.get(name=pending_parent_name)
    except:
        pending_parent = None

    if pending_parent:
        # the following line might not be used eventually - need to check
        pending_parent.inactive_child.add(requesting_child)

        # Check if there already exist a pending parent request
        pending_parent_req = ParentReq.objects.filter(sender_group=requesting_child,
                                                      recv_group=pending_parent,
                                                      pending=True)
        
        print 'STATUS: pending_parent_req > ',
        print pending_parent_req

        # If there is no pending membership request, perform a request
        if not pending_parent_req:
            parent_req = ParentReq(sender_group=requesting_child,
                                   recv_group=pending_parent)
            print "STATUS > Pending notification created"
            parent_req.save()
        else: 
            print 'Already a pending parent request.'

        # COMMENTS BY MING: NOT USED!
            """
        # If request is ajax, ??
        if request.is_ajax():
            print "======================"
            return HttpResponse()
        else:
            print "======================="
            return HttpResponseRedirect('/group/' +  group.url);
    print "=============================="
    return HttpResponse(status=400)     
    """
    print "==========EXIT REQ_PARENT============"
    return False

'''
Looks at the wall post that was potentially submitted and, if any data was
submitted, adds that data to the database. Returns an errorMsg if there was a
error, which can be rendered. Returns None otherwise.
'''
@login_required
def handle_submit(request, group):
    errormsg = None
    if request.method == 'POST':
        if not verify_admin(request, group):
            errormsg = "Get outta here, you liar!"
        elif 'post_content' in request.POST and request.POST['post_content']:

            # later insert logic to distinguish events vs announcement
            if 'eventclick' in request.POST and request.POST['eventclick']:
                errormsg = handle_event(group, request)
            else:
                errormsg = handle_ann(group, request)
        else:
            errormsg = "Empty post? Surely you aren't *that* boring."
    return errormsg

'''
Looks at request. If request specifies a post should be deleted / remmoved, then
it's deleted if the requester is the administrator of the author group; if not,
then the post is simply removed from the group's page. 

Don't forget to add authentication to this. Some permissions should be required
to be able to delete a post. 

I realize generally you make server-side changes with POST, not GET. However,
I see no reason to give the user a browser warning about "resubmission" here,
as would be the case with POST.

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
def delete_post(request):
    err_loc = ' See delete_post in the group_page views.py.'
    if request.method == 'POST':
        try:
            group_id = int(request.POST.get('group_id'))
            post_id = int(request.POST.get('post_id'))
            post_type = int(request.POST.get('post_type'))
        except:
            print 'Wall post delete POST data were not valid integers.' + err_loc
            return HttpResponse(status=400)
            
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

def delete_picture(request):
    err_loc = ' See delete_picture in the group_page views.py.'
    if request.method == 'POST':
        try:
            group_id = int(request.POST.get('group_id'))
            picture_id = int(request.POST.get('picture_id'))
        except:
            print 'Picture delete POST data were not valid integers.' + err_loc
            return HttpResponse(status=400)
            
        if group_id and picture_id:
            group = Group.objects.get(id=group_id)

            try: 
                picture = Picture.objects.get(id=picture_id)
                if request.user in group.admins.all():
                    picture.delete()

                return HttpResponse('/group/' + group.name + '/photos/')
            
            except ObjectDoesNotExist:
                print 'Error: Tried to delete non-existent object.' + err_loc
                
    return HttpResponse(status=400)

def verify_admin(request, group):
    groupadmins = group.admins.all()

    if request.user in groupadmins:
        return True
    else:
        return False

def verify_group(group):
    errormsg = None

    if len(group) > 1:
        errormsg = 'Database Error. URL mapped to multiple groups.'
    elif len(group) == 0:
        errormsg = "Group doesn't exist."        

    return errormsg

#######################################
# GROUP PAGE
#######################################
def group_page(request, group_url, partial_form=None, is_group_page=True,
               is_groupinfo_page=False, is_groupphotos_page=False):
    errormsg = None
    context = RequestContext(request)
    if request.user.is_authenticated():
       profile = request.user.get_profile()
    else:
       profile = None

    # check that the url corresponds to a valid group
    group = Group.objects.filter(url=group_url)
    check = verify_group(group)
    if check:
        return render_to_response('error_page.html', {'errormsg': check,}, 
                                  context_instance=context)
    group = group[0] # only one element in queryset

    # get groupinfo associated with this group
    groupinfo = GroupInfo.objects.filter(group=group)
    if not groupinfo:
        groupinfo = GroupInfo(group=group, data='')
    else:
        groupinfo = groupinfo[0]

    #form = upload_file(request, group.url, is_groupphotos_page)
    (form, errormsg) = upload_file(request, group.url, is_groupphotos_page)

    piccount = 0
    pics = group.pictures.all()
    for pic in pics:
        piccount += 1

    # handle editable info submit
    if 'data_submit' in request.POST:
        errormsg = handle_data(groupinfo, group, request)
        
    # handle the wall post that was perhaps submitted
    if 'post_submit' in request.POST:
        errormsg = handle_submit(request, group)
        if errormsg:
            print errormsg

    # get user's subscription status to this group
    #    Note: I deliberately do not catch Profile.DoesNotExist here,
    #    since all logged in users should have a profile
    try:
        profile.subscriptions.get(id=group.id)
        user_is_subscribed = True
    except (Group.DoesNotExist, AttributeError): 
        # Note: attribute error occurs when user is AnonymousUser
        user_is_subscribed = False

    # get user's list of voted posts
    try:
        voted_post_set = profile.get_voted_posts(group)
    except (AttributeError):
        # Note: attribute error occurs when user is AnonymousUser
        voted_post_set = None

    children = group.child_set.all()

    siblings = []
    if group.parent:
        siblings = group.parent.child_set.all().exclude(name=group.name)

    posts = Filter().get_posts(group) # runs posts through an empty filter
    wall_subtitle = ""
    if not posts:
        wall_subtitle = "Sorry, there are no announcements or events here yet."
    wall_filter_list = Filter.get_wall_filter_list(group.name);
    #annotate(score=hot('post__upvotes', 'post__downvotes', 'post__date')).order_by('score')

    is_admin = False
    if verify_admin(request, group):
        is_admin = True

    is_superadmin = False
    if profile and profile.is_superadmin_of(group):
        is_superadmin = True
    
    membership_status = "notmember"
    if request.user.is_authenticated():
        membership_status = profile.get_membership_status(group)

    posts_on_page = paginate_posts(request, posts)

    return render_to_response('group/base_group.html',
                              {'posts': posts_on_page.object_list, # easy template compatibility
                              'posts_on_page': posts_on_page,
                              'is_admin': is_admin,
                              'is_superadmin': is_superadmin,
                              'is_group_page': is_group_page,
                              'is_groupinfo_page': is_groupinfo_page,
                              'is_groupphotos_page': is_groupphotos_page,
                              'piccount': piccount,
                              'form': form,
                              'errormsg': errormsg,
                              'group': group,
                              'children': children,
                              'siblings': siblings,
                              'groupinfo': groupinfo,
                              'user_is_subscribed': user_is_subscribed,
                              'membership_status': membership_status,
                              'subscribe_view_url':'/_apps/group/views-change_subscribe/',
                              'membership_view_url':'/_apps/group/views-req_membership/',
                              'filter_list': wall_filter_list,
                              'filter_view_url': '/_apps/wall/views-filter_wall/',
                              'delete_post_view_url': '/_apps/group/views-delete_post/',
                              'delete_picture_view_url': '/_apps/group/views-delete_picture/',
                              'voted_post_set': voted_post_set,
                              'wall_subtitle': wall_subtitle,},
                              context_instance=RequestContext(request))

def event_page(request, groupname, title):
    errormsg = None
    
    # check that the url corresponds to a valid event
    this_event = Event.objects.filter(event_url=title)
    group = Group.objects.filter(event = this_event)
    if len(this_event) > 1:
        errormsg = 'Database Error. URL mapped to multiple events.'
        return render_to_response('error_page.html', {'errormsg': errormsg,})
    elif len(this_event) == 0:
        errormsg = "Event doesn't exist."
        return render_to_response('error_page.html', {'errormsg': errormsg,})
    else:
        this_event = this_event[0] # only one element in queryset
    return render_to_response('base_event.html',
                              {'errormsg': errormsg,
                               'event': this_event},
                              context_instance=RequestContext(request))

# REFERENCES:
# http://docs.djangoproject.com/en/dev/topics/forms/modelforms/
#     the above one has info on changing existing objects
#     that should be useful later on when editing content.
# http://docs.djangoproject.com/en/dev/topics/forms/
# http://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound

@login_required
def create_group(request):
    if request.method == 'POST':        
        form = GroupForm(request.POST) # Form bound to POST data
        if form.is_valid(): 

            # Save information of group to be registered but do not commit 
            # to database yet
            new_group = form.save(commit=False)

            # Create the group but prevent parent from being created
            pending_parent_name = new_group.parent
            new_group.parent = None
            new_group.save()

            print "========CREATE_GROUP================"
            print "STATUS > Before entering req_parent"

            # Notify parent group
            req_parent(request, pending_parent_name=pending_parent_name, 
                       requesting_child=new_group)


            print "========EXIT CREATE_GROUP=========="

            #if check is False: # MING: Syntax is correct right
             #   print "ERROR in create_gorup!"


            taglist = request.POST['keywords'].split()
            new_tags = []
            for tags in taglist:
                new_tag, created = Tag.objects.get_or_create(tag=tags)
                if created:
                    new_tag.save()
                new_tags.append(new_tag)

            # associating groupinfo with a group
            info = ''
            groupinfo = GroupInfo(group=new_group,
                                  data=info)
            groupinfo.save()

            # there is probably a more elegant way to associate admin to a group
            currentgroup = Group.objects.get(name=form.cleaned_data['name'])
            currentgroup.addAdmin(request.user)
            currentgroup.addSuperAdmin(request.user)
            currentgroup.save()
                                            
            #name = form.cleaned_data['name']
            #parent = form.cleaned_data['parent']
            #url = form.cleaned_data['url']

            return HttpResponseRedirect('/group/' + form.cleaned_data['url'])

        else:
            return render_to_response('base_groupsignup.html', {'form': form,},
                    RequestContext(request)) # change redirect destination
    else:
        form = GroupForm() # An unbound form - can use this for error messages

    return render_to_response('base_groupsignup.html', {'form': form,}, RequestContext(request))


# TESTING---------------

class UploadFileForm(forms.Form):
    file  = forms.ImageField()
            
def handle_uploaded_file(f, group_url, is_groupphotos_page=False):

    if is_groupphotos_page==False:
        this_group = Group.objects.get(url=group_url)
        names = f.name.split('.')
        f.name = 'profile.' + names[1]
        this_group.img.delete()
        this_group.img = f
        this_group.save()

        # thumbnail--------------------------------------
        image = Image.open(this_group.img)

        image.thumbnail((180, 180), Image.ANTIALIAS)
        image.save(this_group.img.path)
        this_group.img = image 
        # end thumbnail----------------------------------

    else:
        # create picture to establish group name (used in url while uploading)
        pic = Picture.objects.create()
        pic.save() 
        this_group = Group.objects.get(url=group_url)
        this_group.pictures.add(pic)

        # save/upload pic
        pic.image = f
        pic.save()

def upload_file(request, group_url, is_groupphotos_page=False):
    errormsg = None
    if request.method == 'POST' and request.FILES:
        form = UploadFileForm()
        this_group = Group.objects.get(url=group_url)
        if len(this_group.pictures.all()) > 19 and is_groupphotos_page == True:
            errormsg = 'You have reached the maximum number of phots. Try deleting one first.'
        else:
            form = UploadFileForm(request.POST, request.FILES)
            if request.FILES['file'].size > 524288: # 512 KB
                errormsg = 'This image is too large to be uploaded. The size limit is 512KB.'
                return (form, errormsg)
            if form.is_valid():
                handle_uploaded_file(request.FILES['file'], group_url, is_groupphotos_page)
                return (form, errormsg)
            else:
                errormsg = 'Please upload a valid image.'
                #print 'invalid'
    else:
        form = UploadFileForm()

    return (form, errormsg)


#----------------------------------------------------


# groupinfo page
def groupinfo_page(request, groupname):
    return group_page(request, groupname, is_group_page=False, is_groupinfo_page=True, is_groupphotos_page=False)

# groupphotos_page
def groupphotos_page(request, groupname):
    return group_page(request, groupname, is_group_page=False, is_groupinfo_page=False, is_groupphotos_page=True)
    #pass


def handle_data(groupinfo, group, request):
    errormsg = None
    err_loc = ' Error in handle_data in group/views.py.'
    if request.method == 'POST':
        if not verify_admin(request, group):
            errormsg = "You are not an admin!"
            return errormsg

        new_data = request.POST.get('data_content', None)
        if new_data:
            groupinfo.data = new_data
            groupinfo.group = group
            groupinfo.save()

        new_admin = request.POST.get('new_admin', None)
        if new_admin:
            if not request.user.get_profile().is_superadmin_of(group):
                errormsg = 'Only superadmins can add new admins.'
                return errormsg
            
            try: 
                user = User.objects.get(username=new_admin)
            except User.DoesNotExist:
                errormsg = 'Invalid username. User does not exist.'
                return errormsg

            # make sure user is not already admin
            if not user.get_profile().is_admin_of(group):
                group.admins.add(user)
            else:
                errormsg = 'User already an admin.'
                return errormsg

        remove_self = request.POST.get('remove_self', None)
        if remove_self:
            if not request.user.get_profile().is_superadmin_of(group):
                group.admins.remove(request.user)
            else:
                errormsg = "Superadmins can't remove themeselves without " \
                           "first transferring privileges."
                return errormsg                

        num_admins = request.POST.get('num_admins', None)
        if num_admins:
            if not request.user.get_profile().is_superadmin_of(group):
                errormsg = 'Only superadmins can remove other admins.'
                return errormsg
            
            for i in range(0, int(num_admins)):
                remove_admin = request.POST.get('remove_admin-' + str(i), None)
                if remove_admin == 'on':
                    admin_name = request.POST.get('admin-' + str(i), None)
                    try: 
                        user = group.admins.get(username=admin_name)
                    except User.DoesNotExist:
                        errormsg = 'Specified user is not an admin.'
                        return errormsg
                    
                    group.admins.remove(user)

        new_superadmin = request.POST.get('new_superadmin', None)
        if new_superadmin:
            if not request.user.get_profile().is_superadmin_of(group):
                errormsg = 'Only superadmins can transfer their privileges.'
                return errormsg
            
            try: 
                user = User.objects.get(username=new_superadmin)
            except User.DoesNotExist:
                errormsg = 'Invalid username. User does not exist.'
                return errormsg

            if not user.get_profile().is_superadmin_of(group):
                group.superadmins.add(user)
                if not user.get_profile().is_admin_of(group):
                    group.admins.add(user)
            else:
                errormsg = 'User already a superadmin.'
                return errormsg

            group.superadmins.remove(request.user)            
    return errormsg
