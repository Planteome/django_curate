from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# import validators
from django.core.validators import URLValidator

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
        raise ValidationError("This field is not a valid ORCID")

# Create your models here.
class User(AbstractUser):
    affiliation = models.CharField(max_length=255)
    orcid = models.URLField(max_length=40, validators=[URLValidator, orcIDValidator],
                            unique=True,
                            help_text="Example: https://orcid.org/0000-0001-2345-6789")
    has_temp_password = models.BooleanField(default=False)

    # Roles
    ROLE_CHOICES = (
        ("Requestor", "Requestor"),
        ("Contributor", "Contributor"),
        ("Curator", "Curator"),
        ("Moderator", "Moderator"),
        ("Superuser", "Superuser")
    )
    role = models.CharField(
        max_length=12,
        choices=ROLE_CHOICES,
        default="Requestor",
    )

    is_approved = models.BooleanField(default=False)


