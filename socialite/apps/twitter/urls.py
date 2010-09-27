from django.conf.urls.defaults import *
from socialite.apps.twitter import views

urlpatterns = patterns('',
    url(r'^authenticate/$', views.authenticate, name='twitter_authenticate'),
    url(r'^authorize/$', views.authorize, name='twitter_authorize'),
    url(r'^callback/$', views.mediator.callback, name='twitter_callback'),
)
