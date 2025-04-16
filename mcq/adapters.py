from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse

class NoLoginAdapter(DefaultAccountAdapter):
    def login(self, request, *args, **kwargs):
        return redirect(reverse('socialaccount_login', args=['google']))
