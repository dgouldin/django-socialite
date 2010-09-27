from django.conf.urls.defaults import *
from socialite.apps.myspace import views

urlpatterns = patterns('',
    url(r'^authenticate/$', views.authenticate, name='myspace_authenticate'),
    url(r'^authorize/$', views.authorize, name='myspace_authorize'),
    url(r'^callback/$', views.mediator.callback, name='myspace_callback'),
)
