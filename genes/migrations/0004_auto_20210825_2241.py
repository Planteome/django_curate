# Generated by Django 3.2.5 on 2021-08-25 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0003_auto_20210823_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gene',
            name='name',
            field=models.CharField(blank=True, help_text='Example - B-box domain protein 22', max_length=255),
        ),
        migrations.AlterField(
            model_name='gene',
            name='symbol',
            field=models.CharField(blank=True, help_text='Example - BBX22', max_length=255),
        ),
    ]
