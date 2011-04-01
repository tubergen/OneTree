from apps.common.models import ContactForm, GroupForm
from django.shortcuts import render_to_response

# REFERENCES:
# http://docs.djangoproject.com/en/dev/topics/forms/
# http://docs.djangoproject.com/en/dev/ref/forms/api/#ref-forms-api-bound-unbound


def create_group(request):
    if request.method == 'POST':        # To detect submission via POST
        form = GroupForm(request.POST) # Form bound to POST data
        if form.is_valid():   # NEED TO ADD VALIDATION!
                  
            name = form.cleaned_data['name']
            # Need to fill this up

        return HttpResponseRedirect('/group/father') # need to change redirect destination and add RequestContext for CSRF to work
    else:
        form = GroupForm() # An unbound form - can use this for error messages

    return render_to_response('group-signup.html', {'form': form, })
