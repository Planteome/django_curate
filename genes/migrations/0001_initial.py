# Generated by Django 3.2.5 on 2021-08-20 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taxon', '0003_auto_20210813_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='genes/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('gene_id', models.CharField(max_length=255)),
                ('gene_type', models.CharField(blank=True, max_length=255)),
                ('synonyms', models.TextField(blank=True, max_length=2000)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('summary', models.TextField(blank=True, max_length=2000)),
                ('description', models.TextField(blank=True, max_length=2000)),
                ('phenotype', models.CharField(blank=True, max_length=255)),
                ('data_source_object_id', models.CharField(max_length=255)),
                ('data_source_name', models.CharField(max_length=255)),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='taxon.taxon')),
            ],
        ),
    ]
