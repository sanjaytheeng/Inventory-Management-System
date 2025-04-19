from django import template

register = template.Library()

@register.filter
def map_attribute(objects, attribute):
    """Custom template filter to map an attribute from a list of objects."""
    return [getattr(obj, attribute, None) for obj in objects]

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css_class})