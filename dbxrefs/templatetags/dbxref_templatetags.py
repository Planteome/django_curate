from django import template

register = template.Library()


@register.filter(name='dbxref_url_replace')
def dbxref_url_replace(url, id):
    return url.replace('[example_id]', id)


@register.filter(name='example_id_db_remove')
def example_id_db_remove(id, db):
    return id.replace(db + ':', '')
