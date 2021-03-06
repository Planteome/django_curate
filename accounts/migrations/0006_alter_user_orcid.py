# Generated by Django 3.2.5 on 2021-08-25 21:52

import accounts.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_orcid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='orcid',
            field=models.URLField(help_text='Example: https://orcid.org/0000-0001-2345-6789', max_length=40, validators=[django.core.validators.URLValidator, accounts.models.orcIDValidator]),
        ),
    ]
