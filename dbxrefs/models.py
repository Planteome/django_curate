from django.db import models

# Create your models here.
class DBXref(models.Model):
    dbname = models.CharField(max_length=255)
    fullname = models.TextField(max_length=1000)
    genericURL = models.URLField(max_length=255)
    exampleID = models.CharField(max_length=100, null=True, blank=True)
    xrefURL = models.URLField(max_length=255, null=True, blank=True)
    synonyms = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.dbname


class DBXrefDocument(models.Model):
    document = models.FileField(upload_to='dbxrefs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)