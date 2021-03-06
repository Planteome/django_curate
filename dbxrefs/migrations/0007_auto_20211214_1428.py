# Generated by Django 3.2.7 on 2021-12-14 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbxrefs', '0006_alter_dbxref_dbname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbxref',
            name='dbname',
            field=models.CharField(help_text='Example - AGI_LocusCode', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='dbxref',
            name='exampleID',
            field=models.CharField(blank=True, help_text='Example = At2g17950', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='dbxref',
            name='fullname',
            field=models.TextField(help_text='Example - Arabidopsis Genome Initiative', max_length=1000),
        ),
        migrations.AlterField(
            model_name='dbxref',
            name='genericURL',
            field=models.URLField(help_text='Example - http://arabidopsis.org', max_length=255),
        ),
        migrations.AlterField(
            model_name='dbxref',
            name='synonyms',
            field=models.CharField(blank=True, help_text='Example - AGI_Locus', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dbxref',
            name='xrefURL',
            field=models.URLField(blank=True, help_text='Example - http://arabidopsis.org/servlets/TairObject?type=locus&name=[example_id]', max_length=255, null=True),
        ),
    ]
