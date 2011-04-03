from OneTree.apps.helpers.rank_posts import calc_hot_score
from itertools import chain

class Filter:
    valid_filters = ['this_group_only', 'events_only', 'anns_only']

    def __init__(self):
        self.filters = {}

    def add(self, filter_name, value):
        self.filters[filter_name] = value

    def parse_request(self, group, request):
        if request.GET.get('this_group_only'):
            self.filters['this_group_only'] = group;
        if request.GET.get('events_only'):
            self.filters['events_only'] = True;
        return self.filters;

    # Get posts that meet the criteria specified by this filter
    # If anybody knows how to write better filter logic, do it
    def get_posts(self, group):

        only_group = self.filters.get('this_group_only')
        if only_group:
            anns = only_group.announcement_set.all()
            events = only_group.event_set.all()
        else:
            anns = group.announcements.all()
            events = group.events.all()

        if self.filters.get('events_only'):
            anns = None
        elif self.filters.get('anns_only'):
            events = None
        else:
            pass

        # is this inefficient? in future, get/chain ~20 posts instead of all
        try:
            posts = chain(anns, events)
            posts = list(posts)
            posts.sort(key=calc_hot_score, reverse=True)
        except:
            posts = None
        return posts;
