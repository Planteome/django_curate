# Generated by Django 3.2.7 on 2021-09-14 23:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('taxon', '0003_auto_20210813_2237'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('genes', '0006_auto_20210914_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='gene',
            name='changed_by',
            field=models.ForeignKey(default=8, on_delete=django.db.models.deletion.PROTECT, related_name='gene_changed_by', to='accounts.user'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='HistoricalGene',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('symbol', models.CharField(blank=True, help_text='Example - BBX22', max_length=255)),
                ('name', models.CharField(blank=True, help_text='Example - B-box domain protein 22', max_length=255)),
                ('gene_id', models.CharField(help_text='Example - AT1G78600', max_length=255)),
                ('gene_type', models.CharField(blank=True, help_text='Example - protein_coding', max_length=255)),
                ('synonyms', models.TextField(blank=True, help_text='Example - DBB3|Double B-Box 3|LZF1', max_length=2000)),
                ('location', models.CharField(blank=True, help_text='Example - Chromosome 1: 29566863 - 29568931', max_length=255)),
                ('summary', models.TextField(blank=True, max_length=2000)),
                ('description', models.TextField(blank=True, max_length=2000)),
                ('phenotype', models.CharField(blank=True, max_length=255)),
                ('data_source_object_id', models.CharField(blank=True, max_length=255)),
                ('data_source_name', models.CharField(blank=True, max_length=255)),
                ('pubmed_id', models.CharField(blank=True, help_text='comma separated if multiple, Example - 12519987,18287693', max_length=32, null=True)),
                ('history_change_reason', models.TextField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('species', models.ForeignKey(blank=True, db_constraint=False, limit_choices_to=models.Q(('rank', 'species'), ('rank', 'subspecies'), _connector='OR'), null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxon.taxon')),
            ],
            options={
                'verbose_name': 'historical gene',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='GeneApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(blank=True, help_text='Example - BBX22', max_length=255)),
                ('name', models.CharField(blank=True, help_text='Example - B-box domain protein 22', max_length=255)),
                ('gene_id', models.CharField(help_text='Example - AT1G78600', max_length=255)),
                ('gene_type', models.CharField(blank=True, help_text='Example - protein_coding', max_length=255)),
                ('synonyms', models.TextField(blank=True, help_text='Example - DBB3|Double B-Box 3|LZF1', max_length=2000)),
                ('location', models.CharField(blank=True, help_text='Example - Chromosome 1: 29566863 - 29568931', max_length=255)),
                ('summary', models.TextField(blank=True, max_length=2000)),
                ('description', models.TextField(blank=True, max_length=2000)),
                ('phenotype', models.CharField(blank=True, max_length=255)),
                ('data_source_object_id', models.CharField(blank=True, max_length=255)),
                ('data_source_name', models.CharField(blank=True, max_length=255)),
                ('pubmed_id', models.CharField(blank=True, help_text='comma separated if multiple, Example - 12519987,18287693', max_length=32, null=True)),
                ('datetime', models.DateTimeField()),
                ('comments', models.TextField(blank=True, null=True)),
                ('species', models.ForeignKey(limit_choices_to=models.Q(('rank', 'species'), ('rank', 'subspecies'), _connector='OR'), on_delete=django.db.models.deletion.PROTECT, to='taxon.taxon')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
