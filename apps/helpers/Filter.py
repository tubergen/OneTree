from OneTree.apps.helpers.rank_posts import calc_hot_score
from itertools import chain

wall_filter_ids = ['this_group_only', 'events_only', 'anns_only'];
wall_filter_descrips = ["{{group}}'s Posts Only", 'Events Only', 'Announcements Only']

class Filter:
    @staticmethod
    def get_wall_filter_list(group_name):
        updated_filter_descrips = wall_filter_descrips
        updated_filter_descrips[0] = updated_filter_descrips[0].replace("{{group}}", group_name)
        return dict(zip(wall_filter_ids, updated_filter_descrips));

    ''' This is pathetically lazy and at least the names should be changed later.'''
    @staticmethod
    def get_newsfeed_filter_list():
        return dict(zip(wall_filter_ids[1:3], wall_filter_descrips[1:3]));

    def __init__(self):
        self.filters = {}

    def add(self, filter_name, value):
        self.filters[filter_name] = value

    def parse_request(self, group, request):
        if request.GET.get('this_group_only'):
            self.filters['this_group_only'] = group;
        if request.GET.get('events_only'):
            self.filters['events_only'] = True;
        if request.GET.get('anns_only'):
            self.filters['anns_only'] = True;            
        return self.filters;

    # returns a tuple (events, announcements) based on this_group_only
    # filter, if it's set
    def this_group_only(self, group):
        only_group = self.filters.get('this_group_only')
        if only_group:
            anns = only_group.announcement_set.all()
            events = only_group.event_set.all()
        else:
            anns = group.announcements.all()
            events = group.events.all()

        return anns, events;

    # returns a list of posts based on events_only and anns_only filters,
    # if they're set
    def post_type_only(self, anns, events):
        events_only = self.filters.get('events_only')
        anns_only = self.filters.get('anns_only')
        if events_only and anns_only:
            posts = None
        elif anns_only:
            posts = anns
        elif events_only:
            posts = events
        else:
            posts = chain(anns, events)
            
        return posts
    
    # Get posts that meet the criteria specified by this filter
    # If anybody knows how to write better filter logic, do it
    def get_posts(self, group):

        anns, events = self.this_group_only(group)        

        posts = self.post_type_only(anns, events)
        
        # is this inefficient? in future, get/chain ~20 posts instead of all
        try:
            posts = list(posts)
            posts.sort(key=calc_hot_score, reverse=True)
        except:
            print "Failed to form a list of posts in filter.py getFilter()."
            posts = None
        return posts;
