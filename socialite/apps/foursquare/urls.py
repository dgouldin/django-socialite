from django.conf.urls.defaults import *
from socialite.apps.foursquare import views

urlpatterns = patterns('',
    url(r'^authenticate/$', views.authenticate, name='foursquare_authenticate'),
    url(r'^authorize/$', views.authorize, name='foursquare_authorize'),
    url(r'^callback/$', views.mediator.callback, name='foursquare_callback'),
)
