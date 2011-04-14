from OneTree.apps.group_signup.models import GroupForm
from OneTree.apps.common.models import Tag # testing
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from OneTree.apps.common.models import Group


# REFERENCES:
# http://docs.djangoproject.com/en/dev/topics/forms/modelforms/
#     the above one has info on changing existing objects
#     that should be useful later on when editing content.
# http://docs.djangoproject.com/en/dev/topics/forms/
# http://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound

def create_group(request):
    if not request.user.is_authenticated():
        return render_to_response("base_loginerror.html", RequestContext(request));
    if request.method == 'POST':        

        form = GroupForm(request.POST) # Form bound to POST data
        if form.is_valid():   # NEED TO ADD VALIDATION!

            # Save information of group to be registered
            new_group = form.save(commit=False)

            print new_group.parent

            # Get parent group
            try:
                parent = Group.objects.get(name=new_group.parent)
                print 'parent is: ',
                print parent
            except:
                pass 

            # Create the group but prevent parent from being created
            new_group.parent = None
            new_group.save()

            # Add parent to inactive parent list
            try: 
                group = Group.objects.get(url=new_group.url)
                print 'New group created: ',
                print group
                group.inactive_parent = parent
                group.save()
            except:
                pass
            

            taglist = request.POST['keywords'].split()
            new_tags = []
            for tags in taglist:
                new_tag, created = Tag.objects.get_or_create(tag=tags)
                if created:
                    new_tag.save()
                new_tags.append(new_tag)

            new_group = form.save()
            for tag in new_tags:
                new_group.tags.add(tag)


            # there is probably a more elegant way to associate admin to a group
            currentgroup = Group.objects.get(name=form.cleaned_data['name'])
            currentgroup.addAdmin(request.user)
            currentgroup.save()
                                            
            #name = form.cleaned_data['name']
            #parent = form.cleaned_data['parent']
            #url = form.cleaned_data['url']

            # is this all? should we "clean the data"? what does
            # validation actually do?? it seems to work.
            return HttpResponseRedirect('/group/' + form.cleaned_data['url'])

        else:
            return render_to_response('base_groupsignup.html', {'form': form,},
                    RequestContext(request)) # change redirect destination
    else:
        form = GroupForm() # An unbound form - can use this for error messages

    return render_to_response('base_groupsignup.html', {'form': form,}, RequestContext(request))
