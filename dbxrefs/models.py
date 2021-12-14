from django.db import models

# Create your models here.
class DBXref(models.Model):
    dbname = models.CharField(max_length=255, unique=True, help_text="Example - AGI_LocusCode")
    fullname = models.TextField(max_length=1000, help_text="Example - Arabidopsis Genome Initiative")
    genericURL = models.URLField(max_length=255, help_text="Example - http://arabidopsis.org")
    exampleID = models.CharField(max_length=100, null=True, blank=True, help_text="Example - At2g17950")
    xrefURL = models.URLField(max_length=255, null=True, blank=True, help_text="Example - http://arabidopsis.org/servlets/TairObject?type=locus&name=[example_id]")
    synonyms = models.CharField(max_length=255, null=True, blank=True, help_text="Example - AGI_Locus")

    def __str__(self):
        return self.dbname


class DBXrefDocument(models.Model):
    document = models.FileField(upload_to='dbxrefs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)