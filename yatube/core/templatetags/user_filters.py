from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def uglify(field, css=None):
    res: str = ''
    for i in field:
        if (field.index(i) + 1) % 2 == 0:
            res += i.upper()
        else:
            res += i.lower()
    return res


@register.filter
def first_of_many(list):
    return list[0]
