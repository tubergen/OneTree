from OneTree.apps.helpers.rank_posts import calc_hot_score
from OneTree.apps.helpers.enums import PostType
from itertools import chain
from operator import attrgetter
import Queue

filter_ids = ['this_group_only', 'events_only', 'anns_only'];
filter_descrips = ["{{group}}'s posts", 'events', 'announcements']

class Filter:
    @staticmethod
    def get_wall_filter_list(group_name):
        updated_filter_descrips = filter_descrips
        updated_filter_descrips[0] = updated_filter_descrips[0].replace("{{group}}", group_name)
        return dict(zip(filter_ids, updated_filter_descrips));

    @staticmethod
    def get_newsfeed_filter_list():
        return dict(zip(filter_ids[1:3], filter_descrips[1:3]));

    def __init__(self):
        self.filters = {}

    def add(self, filter_name, value):
        self.filters[filter_name] = value

    ''' Parses the request, setting the filters to True as specified. '''
    def parse_request(self, request):
        print 'hi'
        for filter_id in filter_ids:
            if request.GET.get(filter_id):
                self.filters[filter_id] = True
        return self.filters;

    '''
    Returns a tuple (events, announcements) based on this_group_only
    filter, if it's set. We use the group passed into this group_only
    as our only_group, but the parameter group is probably just as good.
    Consider refactoring this later.
    '''
    def this_group_only(self, group):
        only_group = self.filters.get('this_group_only')
        if only_group:
            anns = group.announcement_set.all()
            events = group.event_set.all()
        else:
            anns = group.announcements.all()
            events = group.events.all()

        return anns, events;

    '''
    Returns a list of posts based on events_only and anns_only filters,
    if they're set
    '''
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

    '''
    Returns a list of events that occur on the date specified.
    '''
    def this_date_only(self, date):
       pass 

    '''
    Get posts that meet the criteria specified by this filter
    If anybody knows how to write better filter logic, do it
    '''
    def get_posts(self, group):

        # note that this filters only try to apply these filters
        # they have no effect if the filters are not set
        anns, events = self.this_group_only(group)        
        posts = self.post_type_only(anns, events)
        
        # is this inefficient? in future, get/chain ~20 posts instead of all
        try:
            posts = list(posts)
            # primary sort is hot score, secondary sort is date
            posts.sort(key=attrgetter('date'), reverse=True)            
            posts.sort(key=calc_hot_score, reverse=True)
        except:
            print ("Failed to form a list of posts in filter.py getFilter(), "
                   "perhaps because no posts passed through filter.")
            posts = None
        return posts;

    '''
    Returns a list of top posts from user's subscriptions, which is a
    list of groups. User must exist and have a profile.
    '''
    def get_news(self, user, posts_to_get=10):
        try:
            profile = user.get_profile()
            subscriptions = profile.subscriptions
            removed_events = profile.removed_events
            removed_anns = profile.removed_anns
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
                if post.post_type == PostType.EVENT and \
                       removed_events.filter(id=post.id):
                    continue
                elif post.post_type == PostType.ANNOUNCEMENT and \
                         removed_anns.filter(id=post.id):
                    continue
                else:
                    pass
                
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
        sort primarily on hot score, then on date to keep a stable ordering.
        '''
        if top_posts != None:
            top_posts.sort(key=attrgetter('date'), reverse=True)
            top_posts.sort(key=calc_hot_score, reverse=True)
        return top_posts    
