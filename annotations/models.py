from django.db import models
from django.db.models import Q

# import history models
from simple_history.models import HistoricalRecords

# model imports
from accounts.models import User
from taxon.models import Taxon
from genes.models import Gene
from dbxrefs.models import DBXref

# choices imports
import curate.choices as choices


# Create your models here.
# Model for ontology terms
# Not looking for full tree or anything, just want to be able to search for them by keywords
class AnnotationOntologyTerm(models.Model):
    onto_term = models.CharField(max_length=16, blank=False, unique=True, help_text='GO:0003993', verbose_name='Ontology ID')
    term_name = models.TextField(max_length=1000, blank=True, help_text='Term name', verbose_name='Ontology term name')
    term_definition = models.TextField(max_length=1000, blank=True, help_text='Definition of ontology term', verbose_name='Ontology Term definition')
    term_synonyms = models.TextField(max_length=1000, blank=True, help_text='Term synonyms', verbose_name='Ontology Term synonym')
    term_is_obsolete = models.BooleanField(default=False)
    aspect = models.PositiveSmallIntegerField(choices=choices.AspectCode.choices, blank=False, default=99)

    def __str__(self):
        return self.onto_term


# abstract model for both annotations and those awaiting approval
class AbstractAnnotation(models.Model):
    db = models.ForeignKey(DBXref, on_delete=models.PROTECT, help_text='UniProtKB', verbose_name='Database')
    db_obj_id = models.CharField(max_length=255, blank=False, help_text='P12345', verbose_name='Database object ID')
    db_obj_symbol = models.CharField(max_length=255, blank=False, help_text='PHO3', verbose_name='Database object symbol')
    qualifier = models.CharField(max_length=255, blank=True, help_text='NOT')
    ontology_term = models.ForeignKey(AnnotationOntologyTerm, on_delete=models.PROTECT, help_text='GO:0003993', verbose_name='Ontology ID')
    db_reference = models.CharField(max_length=255, blank=False, help_text='PMID:2676709', verbose_name='Reference DB')
    evidence_code = models.PositiveSmallIntegerField(choices=choices.EvidenceCode.choices, blank=False, help_text='IMP')
    with_from = models.TextField(max_length=1000, blank=True, help_text='GO:0000346', verbose_name='With/From')
    aspect = models.PositiveSmallIntegerField(choices=choices.AspectCode.choices, blank=False, help_text='GO Cellular component')
    db_obj_name = models.TextField(max_length=1000, blank=True, help_text='Toll-like receptor 4', verbose_name='DB object name')
    db_obj_synonym = models.TextField(max_length=1500, blank=True, help_text='hToll', verbose_name='DB synonyms')
    db_obj_type = models.PositiveSmallIntegerField(choices=choices.AnnotationObject.choices, blank=False, help_text='protein', verbose_name='DB object type')
    taxon = models.ForeignKey(Taxon, on_delete=models.PROTECT, help_text='3702')
    date = models.DateField(auto_now=False, auto_now_add=False)
    assigned_by = models.CharField(max_length=255, blank=False, help_text='SGD')
    annotation_extension = models.CharField(max_length=255, blank=True, help_text='part_of(CL:0000576)')
    gene_product_form_id = models.CharField(max_length=255, blank=True, help_text='UniProtKB:P12345-2')

    # foreign key to actual gene in db, could be from db_obj_id, symbol, name, synonym
    # will assign as part of the loading task if found
    internal_gene = models.ForeignKey(Gene, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        abstract = True


# primary annotation model
class Annotation(AbstractAnnotation):
    changed_by = models.ForeignKey(User, blank=False, null=False, on_delete=models.PROTECT,
                                   related_name='annotation_changed_by')
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    def __str__(self):
        return self.db_obj_id


# Approval model (inherited from abstract gene model)
class AnnotationApproval(AbstractAnnotation):
    datetime = models.DateTimeField(blank=False)
    comments = models.TextField(blank=True, null=True)

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
                                  related_name='annotation_requestor')

    source_annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.db_obj_id


class AnnotationDocument(models.Model):
    document = models.FileField(upload_to='annotations/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
