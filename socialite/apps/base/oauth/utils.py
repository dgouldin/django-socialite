from django.contrib.auth.models import User

def get_unique_username(username, user_id=None):
    suffix = 0
    found = True
    new_username = username
    while found:
        qs = User.objects.filter(username=new_username)
        if user_id is not None:
            qs = qs.exclude(pk=user_id)
        if not qs.exists():
            found = False
        else:
            suffix += 1
            new_username = '%s%s' % (username, str(suffix))
    return new_username
