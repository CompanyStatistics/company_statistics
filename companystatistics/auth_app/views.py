from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.db import transaction
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, permissions, generics

from .forms import CSUserLoginForm, CSUserEditForm, CSUserProfileEditForm
from .models import CSUser, CSUserProfile
from .serializers import CSUserSerializer


class UserLoginView(View):
    login_form = CSUserLoginForm
    # initial = {'key': 'value'}
    template_name = 'auth_app/login.html'
    title = 'вход'

    def get(self, request, *args, **kwargs):
        next = request.GET['next'] if 'next' in request.GET.keys() else ''

        context = {
            'page_title': self.title,
            'login_form': self.login_form,
            'next': next,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        login_form = self.login_form(data=request.POST)
        if login_form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            # next = request.POST['next'] if 'next' in request.POST.keys() else ''
            if user:
                login(request, user)
                if 'next' in request.POST.keys():
                    # if 'next' in request.POST.keys() and request.POST['next']:
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return HttpResponseRedirect(reverse('department_list'))
                    # return HttpResponseRedirect(reverse('auth_app:user_department_list'))

        context = {
            'page_title': self.title,
            'login_form': login_form,
            'next': '',
        }

        return render(request, self.template_name, context)


class UserLogoutView(View):
    context = {
        'page_title': 'выход',
    }

    template_name = 'auth_app/logged_out.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, self.template_name, self.context)


@method_decorator(login_required, name='dispatch')
@method_decorator(transaction.atomic, name='dispatch')
class UserEditView(View):
    edit_form = CSUserEditForm
    profile_form = CSUserProfileEditForm
    template_name = 'auth_app/edit.html'
    title = 'редактировать'

    def get(self, request, *args, **kwargs):
        edit_form = self.edit_form(instance=request.user)
        profile_form = self.profile_form(
            instance=request.user.csuserprofile
        )

        context = {
            'page_title': self.title,
            'edit_form': edit_form,
            'profile_form': profile_form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        edit_form = self.edit_form(request.POST, request.FILES, instance=request.user)
        profile_form = self.profile_form(request.POST, instance=request.user.csuserprofile)
        if edit_form.is_valid() and profile_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('auth_app:edit'))

        context = {
            'page_title': self.title,
            'edit_form': edit_form,
            'profile_form': profile_form
        }

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    edit_form = CSUserEditForm
    profile_form = CSUserProfileEditForm
    template_name = 'auth_app/profile.html'
    title = 'профиль'

    def get(self, request, *args, **kwargs):
        edit_form = self.edit_form(instance=request.user)
        profile_form = self.profile_form(
            instance=request.user.csuserprofile
        )

        context = {
            'page_title': self.title,
            'edit_form': edit_form,
            'profile_form': profile_form
        }

        return render(request, self.template_name, context)


# class CSPasswordResetView(PasswordResetView):
#     success_url = reverse_lazy('auth_app:password_reset_done')
#
#
# class CSPasswordResetConfirmView(PasswordResetConfirmView):
#     success_url = reverse_lazy('auth_app:password_reset_complete')
#
#
# class CSPasswordChangeView(PasswordChangeView):
#     success_url = reverse_lazy('auth_app:password_change_done')


class CSUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cs_users to be viewed or edited.
    """
    queryset = CSUser.objects.all().order_by('-date_joined')
    serializer_class = CSUserSerializer
    permission_classes = [permissions.IsAuthenticated]
