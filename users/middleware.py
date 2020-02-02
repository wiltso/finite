from django.contrib.auth.models import User
from django.utils.timezone import now
from django.shortcuts import redirect
from users.models import Profile


ALLOWED_TEARMS_PATHS = ['/users/newTerms/',
                        '/users/accepted/newterms/',
                        '/users/logout/',
                        '/Media/menu.svg']


# Updates the stats of that user
# Also looksthe the users is has accepted the new tearms and conditions
class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            accessAmount = Profile.objects.filter(pk=request.user.pk).values('accessamount')[0]

            Profile.objects.filter(
                pk=request.user.pk
            ).update(
                accessamount=accessAmount['accessamount'] + 1
            )

            Profile.objects.filter(user__id=request.user.pk).update(last_access=now())

            user = User.objects.get(pk=request.user.pk)

            if request.path not in ALLOWED_TEARMS_PATHS:
                if not user.profile.acceptedlatest:
                    return redirect("newTermsAcceppted")
