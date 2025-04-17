from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class InstantLoginAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If already logged in, or account exists, proceed as normal
        if request.user.is_authenticated or sociallogin.is_existing:
            return

        # No need to override process
        # Let Allauth do its job (with SOCIALACCOUNT_AUTO_SIGNUP = True)
        pass
