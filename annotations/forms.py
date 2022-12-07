from django import forms

# models import
from .models import Annotation, AnnotationDocument, AnnotationApproval
from taxon.models import Taxon


# classes
class AnnotationImportDocumentForm(forms.ModelForm):
    document = forms.FileField(label="Annotation file (gaf 2.0 or higher)")
    class Meta:
        model = AnnotationDocument
        fields = ('document',)


class AnnotationAddForm(forms.ModelForm):
    class Meta:
        model = AnnotationApproval
        exclude = ['datetime', 'action', 'status', 'requestor', 'internal_gene', 'source_annotation', 'assigned_by', 'date']
        #TODO: add search for gene in db

    taxon = forms.ModelChoiceField(
        queryset=Taxon.objects.order_by('name').filter(rank__contains='species'))


class AnnotationEditForm(forms.ModelForm):
    class Meta:
        model = AnnotationApproval
        fields = '__all__'
