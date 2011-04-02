import django.dispatch

post_register_service = django.dispatch.Signal(providing_args=["instance", "user_info"])
