# Generated by Django 3.2.7 on 2021-09-15 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0009_geneapproval_requestor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geneapproval',
            name='approver',
        ),
    ]
