from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core import serializers

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

def ajax_search_results(request):
    if request.is_ajax():
        if request.method == 'POST':

            #!!!!!!!!!!!!!!!!!!!!! clean the data ????????
            value = request.POST['value']

            # if we can filter for just 5 results that'd be ideal
            results = complete_indexer.search(value + '*.').spell_correction()
            results_list = []
            for hit in results:
                results_list.append(hit.instance);
                if len(results_list) > 5:
                    break

            data = serializers.serialize('json',
                    results_list, fields=('name', 'url'))
            return HttpResponse(data, mimetype='application/json')
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

def search(request):
    results = []

    if request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            indexer = complete_indexer
            results = indexer.search(query).spell_correction()
            for hit in results:
                print hit.instance.name
    else:
        form = SearchForm()

    return render_to_response('search/search.html',
            {'results': results, 'form': form}, context_instance=RequestContext(request))
