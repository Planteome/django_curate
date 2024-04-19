from django.db import models
from django.db.models import Q

# import history models
from simple_history.models import HistoricalRecords

# model imports
from accounts.models import User
from taxon.models import Taxon

# choices imports
import curate.choices as choices


# Create your models here.
#abstract model for gene for both the actual gene and those waiting to be approved
class AbstractGene(models.Model):
    symbol = models.CharField(max_length=255, blank=True, help_text='Example - BBX22')
    name = models.CharField(max_length=255, blank=True, help_text='Example - B-box domain protein 22')
    gene_id = models.CharField(max_length=255, help_text='Example - AT1G78600')
    gene_type = models.PositiveSmallIntegerField(choices=choices.GeneType.choices, blank=True, help_text='Example - protein_coding')
    species = models.ForeignKey(Taxon, on_delete=models.PROTECT, limit_choices_to=Q(rank='species') | Q(rank='subspecies'))
    synonyms = models.TextField(max_length=2000, blank=True, help_text='Example - DBB3|Double B-Box 3|LZF1')
    location = models.CharField(max_length=255, blank=True, help_text='Example - Chromosome 1: 29566863 - 29568931')
    summary = models.TextField(max_length=2000, blank=True)
    description = models.TextField(max_length=2000, blank=True)
    phenotype = models.CharField(max_length=255, blank=True)
    data_source_object_id = models.CharField(max_length=255, blank=True)
    data_source_name = models.CharField(max_length=255, blank=True)
    pubmed_id = models.CharField(max_length=32, blank=True, null=True, help_text='comma separated if multiple, Example - 12519987,18287693')

    class Meta:
        abstract = True


# primary gene model
class Gene(AbstractGene):
    changed_by = models.ForeignKey(User, blank=False, null=False, on_delete=models.PROTECT,
                                   related_name='gene_changed_by')
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    def __str__(self):
        return self.gene_id


# imported aliases that didn't find gene in db
class MissingGenesFromAliasesImport(models.Model):
    datetime = models.DateTimeField(blank=False)
    missingGeneList = models.TextField(null=True)
    aliasCount = models.IntegerField()


# Approval model (inherited from abstract gene model)
class GeneApproval(AbstractGene):
    datetime = models.DateTimeField(blank=False)
    comments = models.TextField(blank=True, null=True)

    source_gene = models.ForeignKey(Gene, on_delete=models.CASCADE)

    action = models.PositiveSmallIntegerField(
        choices=choices.ApprovalActions.choices,
        blank=False,
        default=choices.ApprovalActions.INITIAL
    )
    status = models.PositiveSmallIntegerField(
        choices=choices.ApprovalStates.choices,
        blank=False,
        default=choices.ApprovalStates.PENDING
    )

    requestor = models.ForeignKey(User, blank=False, null=False,
                                  on_delete=models.PROTECT,
                                  related_name='gene_requestor')

    def __str__(self):
        return self.gene_id


class GeneDocument(models.Model):
    document = models.FileField(upload_to='genes/')
    species = models.ForeignKey(Taxon, on_delete=models.PROTECT, limit_choices_to=Q(rank='species') | Q(rank='subspecies'))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['species__name']

