from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# models import
from .models import User

# forms helper import
from crispy_forms.helper import FormHelper


# orcID validator function
def orcIDValidator(url):
    # get the actual orcid part
    orcid = url.split('/')[-1]
    # remove and store the last digit as it is the checksum
    digit = orcid[-1]
    orcid = orcid[:-1]
    # remove dashes
    orcid = orcid.replace('-', '')
    # calculate checksum
    total = 0
    for i in str(orcid):
        total = (total + int(i)) * 2
    remainder = total % 11
    chksum = (12 - remainder) % 11
    if chksum == 10:
        chksum = "X"
    if digit == str(chksum):
        return orcid
    else:
        raise forms.ValidationError("This field is not a valid ORCID")

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email address:')
    first_name = forms.CharField(label='First Name:')
    last_name = forms.CharField(label='Last Name:')
    affiliation = forms.CharField(label='Affiliation:')
    orcid = forms.CharField(label='<a href="https://orcid.org">ORCID</a>', validators=[orcIDValidator],
                            help_text="Example: https://orcid.org/0000-0012-3456-7890")

    autofocus = 'email'

    def signup(self, request, user):
        pass

    # Make sure no usernames with just digits, will mess up the account info lookups
    def clean_username(self):
        username = self.cleaned_data['username']
        if username.isdigit():
            raise forms.ValidationError("Usernames must contain at least one letter")
        return username

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'affiliation', 'orcid']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.affiliation = self.cleaned_data['affiliation']
        user.orcid = self.cleaned_data['orcid']
        user.role = "Requestor"
        user.is_active = False
        user.is_approved = False
        self.approve(user)
        if commit:
            user.save()
        return user

    def approve(self, user):
        # TODO: send email notification

        return True


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''})
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}))


class UserApprovalForm(forms.ModelForm):
    is_approved = forms.CheckboxInput(attrs={'class': 'form-control', 'name': 'approvalChkbox'})
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label='Role')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'affiliation', 'orcid', 'role', 'is_approved')

    def __init__(self, *args, **kwargs):
        super(UserApprovalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'affiliation', 'orcid', 'role']
