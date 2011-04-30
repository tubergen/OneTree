from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext

from OneTree.apps.common.group import *
from OneTree.apps.common.index import complete_indexer

'''
MODEL_MAP = {
    'group': Group,
    'parent': Group,
}

MODEL_CHOICES = [('', 'all')] + zip(MODEL_MAP.keys(), MODEL_MAP.keys())
'''

class SearchForm(forms.Form):
    query = forms.CharField(required=True)
#    model = forms.ChoiceField(choices=MODEL_CHOICES, required=False)

def search(request):
    results = []

    if request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
 #           model = MODEL_MAP.get(form.cleaned_data['model'])

#            if not model:
            indexer = complete_indexer
#            else:
 #               indexer = model.indexer

            results = indexer.search(query).prefetch()
    else:
        form = SearchForm()

    return render_to_response('search/search.html',
            {'results': results, 'form': form}, context_instance=RequestContext(request))
