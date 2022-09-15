from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from .models import User


# Subclass the OIDCAuthenticationBackend with our own functions to make sure the orcid matches the user account
class MyOIDCAB(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        orcid = claims.get('id')
        if not orcid:
            return self.User.objects.none()
        try:
            user = User.objects.get(orcid=orcid)
            return [user]
        except User.DoesNotExist:
            return self.User.objects.none()

# Both of these are needed, not sure why. But it fails without both.
    def verify_claims(self, claims):
        try:
            user = User.objects.get(orcid=claims.get('id'))
        except User.DoesNotExist:
            user = None

        if user is not None:
            orcid_match = claims.get('sub',[]) in user.orcid
        else:
            orcid_match = False
        return orcid_match