from OneTree.apps.helpers.rank_posts import calc_hot_score
from itertools import chain
import Queue

from operator import attrgetter

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

    # Returns a tuple (events, announcements) based on this_group_only
    # filter, if it's set. We use the group passed into this group_only
    # as our only_group, but the parameter group is probably just as good.
    # Consider refactoring this later.
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

        # note that this filters only try to apply these filters
        # they have no effect if the filters are not set
        anns, events = self.this_group_only(group)        
        posts = self.post_type_only(anns, events)
        
        # is this inefficient? in future, get/chain ~20 posts instead of all
        try:
            posts = list(posts)
            posts.sort(key=calc_hot_score, reverse=True)
        except:
            print ("Failed to form a list of posts in filter.py getFilter(), "
                   "perhaps because no posts passed through filter.")
            posts = None
        return posts;

    # returns a list of top posts from user's subscriptions, which is a
    # list of groups. User must exist and have a profile.
    def get_news(self, user, posts_to_get=10):
        try:
            profile = user.get_profile()
            subscriptions = profile.subscriptions
            deleted_events = profile.deleted_events
            deleted_anns = profile.deleted_anns
        except AttributeError:
            print 'Error: User is either None or Anonymous'
            return None
        
        # add to tuples to pq of the form (score, post)
        # pq is sorted by score from lowest to highest
        pq = Queue.PriorityQueue(posts_to_get)
        for group in subscriptions.all():
            posts = self.get_posts(group)            
            if posts == None:
                continue
            for post in posts:
                # skip this post if it's been deleted
                if deleted_events.filter(id=post.id) or \
                       deleted_anns.filter(id=post.id):
                    continue
                
                score = calc_hot_score(post)
                try: 
                    pq.put_nowait((score, post))
                except Queue.Full:
                    (low_score, low_post) = pq.get_nowait()
                    # keep the post with the higher score
                    # if there's a tie, most recent posts should be put on pq,
                    # but I don't think this is happening right now
                    if low_score < score:
                        pq.put_nowait((score, post))
                    else:
                        pq.put_nowait((low_score, low_post))

        top_posts = []
        while True:
            try:
                (low_score, low_post) = pq.get_nowait()
                top_posts.append(low_post)
            except Queue.Empty:
                break

        '''
        We could just reverse top posts here. However, then the ordering of
        posts will change on filter click if posts have equal scores (of 0). So
        sort first on the post date, THEN sort on calc_hot_score to keep a stable
        ordering.
        '''
        if top_posts != None:
            top_posts.sort(key=attrgetter('date'), reverse=True)
            posts.sort(key=calc_hot_score, reverse=True)
        return top_posts    
