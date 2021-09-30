# Generated by Django 3.2.7 on 2021-09-15 20:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('genes', '0008_auto_20210915_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='geneapproval',
            name='requestor',
            field=models.ForeignKey(default=8, on_delete=django.db.models.deletion.PROTECT, related_name='gene_requestor', to='accounts.user'),
            preserve_default=False,
        ),
    ]
