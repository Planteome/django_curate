from django import forms

# models import
from .models import DBXref, DBXrefDocument


class DBXrefImportDocumentForm(forms.ModelForm):
    document = forms.FileField(required=False, label="Database xrefs (external references) file")
    document_URL = forms.URLField(required=False, label="Database xrefs URL (must be raw file format)")
    class Meta:
        model = DBXrefDocument
        fields = ('document','document_URL')

    def clean(self):
        cleaned_data = super().clean()
        document = cleaned_data.get("document")
        document_URL = cleaned_data.get("document_URL")
        if document and document_URL:
            raise forms.ValidationError({"document_URL": "Either upload a file or supply a URL, but not both"})
        if not document and not document_URL:
            raise forms.ValidationError({"document_URL": "At least one of these need to be entered"})
        if document_URL:
            print("here")



class DBXrefAddForm(forms.ModelForm):
    class Meta:
        model = DBXref
        fields = '__all__'


class DBXrefEditForm(forms.ModelForm):
    class Meta:
        model = DBXref
        fields = '__all__'