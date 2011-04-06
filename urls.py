from django.conf.urls.defaults import *
from OneTree.apps.group_page.views import group_page
from OneTree.apps.user_page.views import user_page
from OneTree.apps.user_signup.views import create_user
from OneTree.apps.group_signup.views import create_group
from OneTree.apps.common.views import homepage
from OneTree.apps.wall.views import *
from django.conf import settings
from django.contrib.auth.views import login, logout

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
    (r'^group-signup/$', create_group),
    (r'^_apps/wall/views-update_vote/$', update_vote),
    (r'^_apps/wall/views-filter_wall/$', filter_wall),                       
    (r'^user-signup/$', create_user),
    (r'^login/$',  login, {'template_name': 'base_login.html'}),
    (r'^logout/$', logout, {'next_page': '/login/'}), # change this to the homepage when we have one...
    (r'^profile/$', user_page, {'username': ''}),
    (r'^$', homepage),
)

# on our own computers, serve static files properly
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        )

