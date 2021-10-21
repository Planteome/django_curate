# Generated by Django 3.2.7 on 2021-10-15 21:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('genes', '0012_auto_20211005_1133'),
        ('taxon', '0003_auto_20210813_2237'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dbxrefs', '0006_alter_dbxref_dbname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_obj_id', models.CharField(help_text='P12345', max_length=255, verbose_name='Database object ID')),
                ('db_obj_symbol', models.CharField(help_text='PHO3', max_length=255, verbose_name='Database object symbol')),
                ('qualifier', models.CharField(blank=True, help_text='NOT', max_length=255)),
                ('ontology_id', models.CharField(help_text='GO:0003993', max_length=16)),
                ('db_reference', models.CharField(help_text='PMID:2676709', max_length=255, verbose_name='Reference DB')),
                ('evidence_code', models.PositiveSmallIntegerField(choices=[(1, 'Inferred from Expression Pattern'), (2, 'Inferred from Direct Assay'), (3, 'Inferred from Mutant Phenotype'), (4, 'Inferred from Genetic Interaction'), (5, 'Inferred from Physical Interaction'), (6, 'Inferred by Association of Genotype from Phenotype'), (7, 'Inferred by Curator'), (8, 'Inferred from Electronic Annotation'), (9, 'Inferred from Sequence or structural Similarity'), (10, 'Non-traceable Author Statement'), (11, 'Traceable Author Statement'), (12, 'No biological Data available'), (13, 'Inferred from Sequence Model'), (14, 'Inferred from Reviewed Computational Analysis'), (15, 'Inferred from Experiment'), (16, 'Inferred from High Throughput Experiment'), (17, 'Inferred from High Throughput Direct Assay'), (18, 'Inferred from High Throughput Mutant Phenotype'), (19, 'Inferred from High Throughput Genetic Interaction'), (20, 'Inferred from High Throughput Expression Pattern'), (21, 'Inferred from Biological aspect of Ancestor'), (22, 'Inferred from Biological aspect of Descendant'), (23, 'Inferred from Key Residues'), (24, 'Inferred from Rapid Divergence'), (25, 'Inferred from Sequence Orthology'), (26, 'Inferred from Sequence Alignment'), (27, 'Inferred from Genomic Context')], help_text='IMP')),
                ('with_from', models.TextField(blank=True, help_text='GO:0000346', max_length=1000, verbose_name='With/From')),
                ('aspect', models.PositiveSmallIntegerField(choices=[(1, 'PO Plant Anatomy'), (2, 'PO Plant Growth'), (3, 'TO Trait'), (4, 'PECO Experimental condition'), (5, 'PSO Stress'), (6, 'GO Biological Process'), (7, 'GO Cellular Component'), (8, 'GO Molecular Function')], help_text='GO Cellular component')),
                ('db_obj_name', models.TextField(blank=True, help_text='Toll-like receptor 4', max_length=1000, verbose_name='DB object name')),
                ('db_obj_synonym', models.TextField(blank=True, help_text='hToll', max_length=1500, verbose_name='DB synonyms')),
                ('db_obj_type', models.PositiveSmallIntegerField(choices=[(1, 'protein'), (2, 'germplasm'), (3, 'gene model'), (4, 'mRNA'), (5, 'gene'), (6, 'QTL'), (7, 'gene product'), (8, 'tRNA'), (9, 'miRNA'), (10, 'RNA'), (11, 'antisense_lncRNA'), (12, 'snoRNA'), (13, 'pseudogene'), (14, 'rRNA'), (15, 'snRNA'), (16, 'lnc_RNA'), (17, 'antisense_RNA'), (18, 'uORF')], help_text='protein', verbose_name='DB object type')),
                ('date', models.DateField()),
                ('assigned_by', models.CharField(help_text='SGD', max_length=255)),
                ('annotation_extension', models.CharField(blank=True, help_text='part_of(CL:0000576)', max_length=255)),
                ('gene_product_form_id', models.CharField(blank=True, help_text='UniProtKB:P12345-2', max_length=255)),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='annotation_changed_by', to=settings.AUTH_USER_MODEL)),
                ('db', models.ForeignKey(help_text='UniProtKB', on_delete=django.db.models.deletion.PROTECT, to='dbxrefs.dbxref', verbose_name='Database')),
                ('internal_gene', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='genes.gene')),
                ('taxon', models.ForeignKey(help_text='3702', on_delete=django.db.models.deletion.PROTECT, to='taxon.taxon')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AnnotationDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='annotations/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalAnnotation',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('db_obj_id', models.CharField(help_text='P12345', max_length=255, verbose_name='Database object ID')),
                ('db_obj_symbol', models.CharField(help_text='PHO3', max_length=255, verbose_name='Database object symbol')),
                ('qualifier', models.CharField(blank=True, help_text='NOT', max_length=255)),
                ('ontology_id', models.CharField(help_text='GO:0003993', max_length=16)),
                ('db_reference', models.CharField(help_text='PMID:2676709', max_length=255, verbose_name='Reference DB')),
                ('evidence_code', models.PositiveSmallIntegerField(choices=[(1, 'Inferred from Expression Pattern'), (2, 'Inferred from Direct Assay'), (3, 'Inferred from Mutant Phenotype'), (4, 'Inferred from Genetic Interaction'), (5, 'Inferred from Physical Interaction'), (6, 'Inferred by Association of Genotype from Phenotype'), (7, 'Inferred by Curator'), (8, 'Inferred from Electronic Annotation'), (9, 'Inferred from Sequence or structural Similarity'), (10, 'Non-traceable Author Statement'), (11, 'Traceable Author Statement'), (12, 'No biological Data available'), (13, 'Inferred from Sequence Model'), (14, 'Inferred from Reviewed Computational Analysis'), (15, 'Inferred from Experiment'), (16, 'Inferred from High Throughput Experiment'), (17, 'Inferred from High Throughput Direct Assay'), (18, 'Inferred from High Throughput Mutant Phenotype'), (19, 'Inferred from High Throughput Genetic Interaction'), (20, 'Inferred from High Throughput Expression Pattern'), (21, 'Inferred from Biological aspect of Ancestor'), (22, 'Inferred from Biological aspect of Descendant'), (23, 'Inferred from Key Residues'), (24, 'Inferred from Rapid Divergence'), (25, 'Inferred from Sequence Orthology'), (26, 'Inferred from Sequence Alignment'), (27, 'Inferred from Genomic Context')], help_text='IMP')),
                ('with_from', models.TextField(blank=True, help_text='GO:0000346', max_length=1000, verbose_name='With/From')),
                ('aspect', models.PositiveSmallIntegerField(choices=[(1, 'PO Plant Anatomy'), (2, 'PO Plant Growth'), (3, 'TO Trait'), (4, 'PECO Experimental condition'), (5, 'PSO Stress'), (6, 'GO Biological Process'), (7, 'GO Cellular Component'), (8, 'GO Molecular Function')], help_text='GO Cellular component')),
                ('db_obj_name', models.TextField(blank=True, help_text='Toll-like receptor 4', max_length=1000, verbose_name='DB object name')),
                ('db_obj_synonym', models.TextField(blank=True, help_text='hToll', max_length=1500, verbose_name='DB synonyms')),
                ('db_obj_type', models.PositiveSmallIntegerField(choices=[(1, 'protein'), (2, 'germplasm'), (3, 'gene model'), (4, 'mRNA'), (5, 'gene'), (6, 'QTL'), (7, 'gene product'), (8, 'tRNA'), (9, 'miRNA'), (10, 'RNA'), (11, 'antisense_lncRNA'), (12, 'snoRNA'), (13, 'pseudogene'), (14, 'rRNA'), (15, 'snRNA'), (16, 'lnc_RNA'), (17, 'antisense_RNA'), (18, 'uORF')], help_text='protein', verbose_name='DB object type')),
                ('date', models.DateField()),
                ('assigned_by', models.CharField(help_text='SGD', max_length=255)),
                ('annotation_extension', models.CharField(blank=True, help_text='part_of(CL:0000576)', max_length=255)),
                ('gene_product_form_id', models.CharField(blank=True, help_text='UniProtKB:P12345-2', max_length=255)),
                ('history_change_reason', models.TextField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('db', models.ForeignKey(blank=True, db_constraint=False, help_text='UniProtKB', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='dbxrefs.dbxref', verbose_name='Database')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('internal_gene', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='genes.gene')),
                ('taxon', models.ForeignKey(blank=True, db_constraint=False, help_text='3702', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taxon.taxon')),
            ],
            options={
                'verbose_name': 'historical annotation',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='AnnotationApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_obj_id', models.CharField(help_text='P12345', max_length=255, verbose_name='Database object ID')),
                ('db_obj_symbol', models.CharField(help_text='PHO3', max_length=255, verbose_name='Database object symbol')),
                ('qualifier', models.CharField(blank=True, help_text='NOT', max_length=255)),
                ('ontology_id', models.CharField(help_text='GO:0003993', max_length=16)),
                ('db_reference', models.CharField(help_text='PMID:2676709', max_length=255, verbose_name='Reference DB')),
                ('evidence_code', models.PositiveSmallIntegerField(choices=[(1, 'Inferred from Expression Pattern'), (2, 'Inferred from Direct Assay'), (3, 'Inferred from Mutant Phenotype'), (4, 'Inferred from Genetic Interaction'), (5, 'Inferred from Physical Interaction'), (6, 'Inferred by Association of Genotype from Phenotype'), (7, 'Inferred by Curator'), (8, 'Inferred from Electronic Annotation'), (9, 'Inferred from Sequence or structural Similarity'), (10, 'Non-traceable Author Statement'), (11, 'Traceable Author Statement'), (12, 'No biological Data available'), (13, 'Inferred from Sequence Model'), (14, 'Inferred from Reviewed Computational Analysis'), (15, 'Inferred from Experiment'), (16, 'Inferred from High Throughput Experiment'), (17, 'Inferred from High Throughput Direct Assay'), (18, 'Inferred from High Throughput Mutant Phenotype'), (19, 'Inferred from High Throughput Genetic Interaction'), (20, 'Inferred from High Throughput Expression Pattern'), (21, 'Inferred from Biological aspect of Ancestor'), (22, 'Inferred from Biological aspect of Descendant'), (23, 'Inferred from Key Residues'), (24, 'Inferred from Rapid Divergence'), (25, 'Inferred from Sequence Orthology'), (26, 'Inferred from Sequence Alignment'), (27, 'Inferred from Genomic Context')], help_text='IMP')),
                ('with_from', models.TextField(blank=True, help_text='GO:0000346', max_length=1000, verbose_name='With/From')),
                ('aspect', models.PositiveSmallIntegerField(choices=[(1, 'PO Plant Anatomy'), (2, 'PO Plant Growth'), (3, 'TO Trait'), (4, 'PECO Experimental condition'), (5, 'PSO Stress'), (6, 'GO Biological Process'), (7, 'GO Cellular Component'), (8, 'GO Molecular Function')], help_text='GO Cellular component')),
                ('db_obj_name', models.TextField(blank=True, help_text='Toll-like receptor 4', max_length=1000, verbose_name='DB object name')),
                ('db_obj_synonym', models.TextField(blank=True, help_text='hToll', max_length=1500, verbose_name='DB synonyms')),
                ('db_obj_type', models.PositiveSmallIntegerField(choices=[(1, 'protein'), (2, 'germplasm'), (3, 'gene model'), (4, 'mRNA'), (5, 'gene'), (6, 'QTL'), (7, 'gene product'), (8, 'tRNA'), (9, 'miRNA'), (10, 'RNA'), (11, 'antisense_lncRNA'), (12, 'snoRNA'), (13, 'pseudogene'), (14, 'rRNA'), (15, 'snRNA'), (16, 'lnc_RNA'), (17, 'antisense_RNA'), (18, 'uORF')], help_text='protein', verbose_name='DB object type')),
                ('date', models.DateField()),
                ('assigned_by', models.CharField(help_text='SGD', max_length=255)),
                ('annotation_extension', models.CharField(blank=True, help_text='part_of(CL:0000576)', max_length=255)),
                ('gene_product_form_id', models.CharField(blank=True, help_text='UniProtKB:P12345-2', max_length=255)),
                ('datetime', models.DateTimeField()),
                ('comments', models.TextField(blank=True, null=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'Approve'), (2, 'Reject'), (3, 'More info requested'), (4, 'Initial request, awaiting moderator')], default=4)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Approved'), (3, 'Rejected')], default=1)),
                ('db', models.ForeignKey(help_text='UniProtKB', on_delete=django.db.models.deletion.PROTECT, to='dbxrefs.dbxref', verbose_name='Database')),
                ('internal_gene', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='genes.gene')),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='annotation_requestor', to=settings.AUTH_USER_MODEL)),
                ('source_annotation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='annotations.annotation')),
                ('taxon', models.ForeignKey(help_text='3702', on_delete=django.db.models.deletion.PROTECT, to='taxon.taxon')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
