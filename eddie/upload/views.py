from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext  
from django import forms

class UploadFileForm(forms.Form):
    file  = forms.FileField()
            
def handle_uploaded_file(f):
    destination = open('uploaded_files/' + f.name, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'],)
            return HttpResponseRedirect('/success/')
        else:
            print 'invalid'
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form},
                              context_instance=RequestContext(request))
