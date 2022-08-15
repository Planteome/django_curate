from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse_lazy
from django.views import generic as g
from django.contrib.auth import login
from django.shortcuts import redirect

# models import
from django.views.generic import TemplateView, FormView, UpdateView

from .models import User

# forms import
from .forms import UserRegistrationForm, UserApprovalForm, UserEditForm


# Create your views here.

def index(request):
    return HttpResponse("Welcome to the account setup page.")


class AccountSignupIndexView(g.FormView):
    model = User
    template_name = 'accounts/signup.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        form.save()
        return redirect('accounts:submitted')


class AccountSubmittedView(g.View):
    template_name = 'accounts/submitted.html'

    def get(self, request):
        return render(request, 'accounts/submitted.html')


class AccountApprovalView(FormView):
    model = User
    template_name = 'accounts/approve.html'
    form_class = UserApprovalForm

    def get_context_data(self, **kwargs):
        context = super(AccountApprovalView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context
        # get users that are awaiting approval
        try:
            users = User.objects.filter(is_approved=True)
        except User.DoesNotExist:
            users = None

        context['user_list'] = users
        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False
        return context

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        # list of users to approve
        approve_list = request.POST.getlist('approvalChkbox')
        user_list = request.POST.getlist('username')
        role_list = request.POST.getlist('role')
        # dict to store usernames to selected roles
        role_dict = dict(zip(user_list, role_list))
        for approveUser in approve_list:
            # update the user in the database
            user = User.objects.get(username=approveUser)
            user.is_active = True
            user.is_approved = False
            user.role = role_dict[approveUser]
            if user.role is "Superuser":
                user.is_superuser = True
                user.is_staff = True
            user.save()

        # list of users to delete
        delete_list = request.POST.getlist('deleteChkbox')
        for deleteUser in delete_list:
            user = User.objects.get(username=deleteUser)
            user.delete()
        return redirect('accounts:approve')


class AccountInfoView(TemplateView):
    model = User
    template_name = 'accounts/info.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AccountInfoView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context
        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False

        # lookup the user either by id or username
        if self.kwargs['user'].isdigit():
            try:
                lookup_user = User.objects.get(pk=self.kwargs['user'])
            except User.DoesNotExist:
                lookup_user = None
        else:
            try:
                lookup_user = User.objects.get(username=self.kwargs['user'])
            except User.DoesNotExist:
                lookup_user = None
        context['user'] = lookup_user
        if lookup_user == user:
            context['self_user'] = True
        return context


class AccountUpdateView(UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_edit_form.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AccountUpdateView, self).get_context_data(**kwargs)
        user = self.request.user
        if not user.is_authenticated:
            context['logged_in'] = False
            return context
        context['logged_in'] = True
        if user.is_superuser:
            context['superuser'] = True
        else:
            context['superuser'] = False

        return context

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        # Restrict type of user who can access UpdateView
        if obj.id is self.request.user.id or self.request.user.is_superuser:
            return obj
        else:
            raise PermissionDenied()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            # Disable these fields
            form.fields["username"].disabled = True
            form.fields["role"].disabled = True
        return form

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.request.path_info)
