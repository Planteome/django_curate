from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import views as AuthViews
from .forms import UserLoginForm
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.AccountSignupIndexView.as_view(), name='signup_form'),
    path('submitted/', views.AccountSubmittedView.as_view(), name='submitted'),
    path('approve/', views.AccountApprovalView.as_view(), name='approve'),
    path('info/<slug:user>', views.AccountInfoView.as_view(), name='info'),
    path('edit/<slug:pk>', views.AccountUpdateView.as_view(), name='edit_user'),
    path('login/', views.CustomLoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=UserLoginForm),
        name='login'),
    path('logout/', AuthViews.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('bad_orcid/', AuthViews.LogoutView.as_view(template_name='accounts/bad_orcid.html'), name='bad_orcid'),
    path('password_change/', AuthViews.PasswordChangeView.as_view(
        success_url=reverse_lazy('accounts:password_change_done'),
        template_name='accounts/password_reset_form.html'),
        name='password_change'),
    path('password_change/done/', AuthViews.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'),
        name='password_change_done'),
    path('password_reset/', AuthViews.PasswordResetView.as_view(
        email_template_name='accounts/password_reset_email.html',
        success_url=reverse_lazy('accounts:password_reset_done'),
        template_name='accounts/password_reset_form.html'),
        name='password_reset'),
    path('password_reset/done/', AuthViews.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', AuthViews.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('accounts:password_reset_complete'),
        template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('reset/done/', AuthViews.PasswordResetCompleteView.as_view(
        template_name='accounts/password_change_done.html'),
        name='password_reset_complete'),
    path('', RedirectView.as_view(url='/accounts/login', permanent=False)),
]
