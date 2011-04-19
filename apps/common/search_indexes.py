from OneTree.apps.common.models import Group
from haystack.indexes import *
from haystack import site

class GroupIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    name = CharField(model_attr='name')
    keywords = CharField(model_attr='keywords')
    # avoiding tags because tags are their own model, not just a field.

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Group.objects.all()

site.register(Group, GroupIndex)
