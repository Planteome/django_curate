# Generated by Django 3.2.7 on 2022-09-02 20:51

import accounts.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_rename_needs_approval_user_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='orcid',
            field=models.URLField(help_text='Example: https://orcid.org/0000-0001-2345-6789', max_length=40, unique=True, validators=[django.core.validators.URLValidator, accounts.models.orcIDValidator]),
        ),
    ]
