from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic as g
from django.contrib.auth import login
from django.shortcuts import redirect

# models import
from django.views.generic import TemplateView, FormView

from .models import User

# forms import
from .forms import UserRegistrationForm, UserApprovalForm


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
            users = User.objects.filter(needs_approval=True)
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
        for approveUser in approve_list:
            # update the user in the database
            user = User.objects.get(username=approveUser)
            user.is_active = True
            user.needs_approval = False
            if user.role is "Superuser":
                user.is_superuser = True
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
        return context
