from django import template

# models import
from dbxrefs.models import DBXref

register = template.Library()


@register.filter(name='dbxref_url_replace')
def dbxref_url_replace(url, id):
    return url.replace('[example_id]', id)


@register.filter(name='example_id_db_remove')
def example_id_db_remove(id, db):
    return id.replace(db + ':', '')

@register.filter(name='get_dbxref_url')
def get_dbxref_url(object):
    db = object.split(':')[0]
    id = object.split(':', 1)[1]
    dbxref = DBXref.objects.get(dbname=db)
    return dbxref_url_replace(dbxref.xrefURL, id)

@register.filter(name='get_id_from_dbxref')
def get_id_from_dbxref(object):
    id = object.split(':')[-1]
    return id
