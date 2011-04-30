from django.conf.urls.defaults import *
from OneTree.apps.group.views import group_page, groupinfo_page, groupphotos_page, event_page, delete_post, change_subscribe, delete_picture
from OneTree.apps.user.views import *
from OneTree.apps.notifications.views import notification_page, answer_notif
from OneTree.apps.group.views import create_group, req_membership
from OneTree.apps.common.views import homepage
from OneTree.apps.newsfeed.views import newsfeed, filter_newsfeed, remove_post
from OneTree.apps.wall.views import *
from OneTree.apps.search.views import search
from django.conf import settings
from django.contrib.auth.views import login, logout, password_change, password_change_done, password_reset
from django.views.generic.simple import direct_to_template

#import haystack
import djapian

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#admin.autodiscover()

# get djapian indexing
djapian.load_indexes()

urlpatterns = patterns('',
    # Example:
    # (r'^onetree/', include('onetree.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Administration
    (r'^admin/', include(admin.site.urls)),

    # Group 
    url(r'^group/$', group_page, {'group_url': 'princeton'}), # just default there for now
    (r'^group/(\w+)/$', group_page),
    (r'^group/(\w+)/info/$', groupinfo_page),
    (r'^group/(\w+)/photos/$', groupphotos_page),
    (r'^group/(\w+)/event/(.*)/$', event_page),
    (r'^group-signup/$', create_group),
    (r'^_apps/wall/views-update_vote/$', update_vote),
    (r'^_apps/wall/views-filter_wall/$', filter_wall),
    (r'^_apps/wall/views-delete_comment/$', delete_comment),                  
    (r'^_apps/group/views-change_subscribe/$', change_subscribe),
    (r'^_apps/group/views-req_membership/$', req_membership),                  
    (r'^_apps/newsfeed/views-filter_newsfeed/$', filter_newsfeed),
    (r'^_apps/newsfeed/views-remove_post/$', remove_post),
    (r'^_apps/group/views-delete_post/$', delete_post),  
    (r'^_apps/group/views-delete_picture/$', delete_picture),  

    # User
    (r'^secret-signup/$', create_user),
    (r'^user-signup/$', register),

    url(r'^login/$',  login, {'template_name': 'base_login.html'}, name='auth_login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='auth_logout',),
    url(r'^logout/(?P<next_page>.*)/$', logout, name='auth_logout_next'),
    (r'^profile/$', user_page, {'username': ''}),
    (r'^profile/account/$', user_account, {'username': ''}),
    (r'^profile/account/fill-details/$', complete_profile, ),
    (r'^profile/account/changepwdsuccess/$', password_change_success, ),
    url(r'^profile/account/changepwd/$', password_change, {'template_name': 'user/change_password.html', 'post_change_redirect': '/profile/account/changepwdsuccess' }, name='password_change'),
    (r'^profile/approve/$', admin_approve),
    (r'^profile/account/changeemail/$', change_email, ),
    url(r'^profile/account/forgetpwd/$', password_reset, { }, ), 
    (r'^profile/account/forgetpwdsent/$', forget_password_email_sent, ),
    (r'^news/$', newsfeed),
    (r'^$', homepage),
    (r'^register/$', register),

    # Notifications
    (r'^notifications/$', notification_page),
    (r'^_apps/notifications/views-answer_notif/$', answer_notif),
                       
    # Searching
    #(r'^search/', include('haystack.urls')),
    url(r'^search/$', search, name='search'),

    # Activate/complete must come before activate/activation_key
    url(r'^activate/complete/$', 
        direct_to_template, {'template':'registration/activation_complete.html'},
        name="reg_complete"),
    url(r'^activate/(?P<activation_key>\w+)/$', activate, name="activator"),
    (r'^accounts/', include('OneTree.registration.backends.default.urls')),
    (r'^post/comment/$', post_comment),
                      
)

# on our own computers, serve static files properly
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        )

