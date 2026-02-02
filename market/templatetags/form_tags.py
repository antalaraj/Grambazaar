from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field widget."""
    widget = field.field.widget
    existing = widget.attrs.get('class', '')
    if existing:
        widget.attrs['class'] = f"{existing} {css_class}"
    else:
        widget.attrs['class'] = css_class
    return field
