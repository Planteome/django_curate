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


class AnnotationAddByGeneForm(forms.ModelForm):
    class Meta:
        model = AnnotationApproval
        exclude = ['datetime', 'action', 'status', 'requestor', 'internal_gene', 'source_annotation', 'assigned_by', 'date']

    taxon = forms.ModelChoiceField(
        queryset=Taxon.objects.order_by('name').filter(rank__contains='species'))

    def __init__(self, *args, **kwargs):
        db_obj_id = kwargs.pop('db_obj_id', None)
        taxon = kwargs.pop('taxon', None)
        super(AnnotationAddByGeneForm, self).__init__(*args, **kwargs)
        self.fields['db_obj_id'].initial = db_obj_id
        self.fields['db_obj_id'].widget.attrs['readonly'] = True
        self.fields['db_obj_id'].diabled = True
        self.fields['taxon'].initial = taxon
        self.fields['taxon'].widget.attrs['readonly'] = True
        self.fields['taxon'].diabled = True

class AnnotationEditForm(forms.ModelForm):
    class Meta:
        model = AnnotationApproval
        fields = '__all__'
