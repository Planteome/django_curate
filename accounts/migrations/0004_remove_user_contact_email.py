# Generated by Django 3.2.5 on 2021-07-30 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20210727_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='contact_email',
        ),
    ]
