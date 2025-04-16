from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

class NoLoginAdapter(DefaultAccountAdapter):
    def login(self, request, *args, **kwargs):
        return redirect('/accounts/google/login/?process=login')
