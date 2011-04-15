from django.conf.urls.defaults import *
from OneTree.apps.group_page.views import group_page, event_page, delete_post
from OneTree.apps.user_page.views import user_page
from OneTree.apps.user_signup.views import create_user
from OneTree.apps.group_signup.views import create_group
from OneTree.apps.common.views import homepage
from OneTree.apps.newsfeed.views import newsfeed, change_subscribe, filter_newsfeed, remove_post
from OneTree.apps.wall.views import *
from django.conf import settings
from django.contrib.auth.views import login, logout

from OneTree.apps.user_signup.views import register, activate
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^onetree/', include('onetree.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    #(r'^group/$', group_page),
    (r'^group/(\w+)/$', group_page),
    (r'^user/(\w+)/$', user_page),
    (r'^group/(\w+)/(.*)/$', event_page),
    (r'^group-signup/$', create_group),
    (r'^_apps/wall/views-update_vote/$', update_vote),
    (r'^_apps/wall/views-filter_wall/$', filter_wall),
    (r'^_apps/newsfeed/views-change_subscribe/$', change_subscribe),
    (r'^_apps/newsfeed/views-filter_newsfeed/$', filter_newsfeed),
    (r'^_apps/newsfeed/views-remove_post/$', remove_post),
    (r'^_apps/group_page/views-delete_post/$', delete_post),  
    (r'^user-signup/$', create_user),
    url(r'^login/$',  login, {'template_name': 'base_login.html'}, name='auth_login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='auth_logout',),
    url(r'^logout/(?P<next_page>.*)/$', logout, name='auth_logout_next'),
    (r'^profile/$', user_page, {'username': ''}),
    (r'^newsfeed/$', newsfeed),
    (r'^$', homepage),
    (r'^register/$', register),
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

