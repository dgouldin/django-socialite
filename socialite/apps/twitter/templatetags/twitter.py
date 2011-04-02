from django import template

from socialite.apps.twitter import helper

register = template.Library()

@register.simple_tag()
def twitter_avatar(size, user_id):
    return helper.get_avatar(size, user_id=user_id)
