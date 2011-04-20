from djapian import space, Indexer, CompositeIndexer
from OneTree.apps.common.models import *
from OneTree.apps.common.group import *
from OneTree.apps.common.user import *

class GroupIndexer(Indexer):
    fields = ['name']
    tags = [ # I don't get the difference between fields and tags well :(
            ('name', 'name'),
            ('parent', 'parent'),
    ]

space.add_index(Group, attach_as='indexer')

complete_indexer = CompositeIndexer(Group.indexer)
