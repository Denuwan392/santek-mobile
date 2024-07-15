from django import template
from django.forms.boundfield import BoundField
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='as_bootstrap')
def as_bootstrap(form):
    return mark_safe(form_to_bootstrap(form))

def form_to_bootstrap(form):
    rendered_fields = []
    for field in form:
        rendered_fields.append(field_as_bootstrap(field))
    return "\n".join(rendered_fields)

def field_as_bootstrap(field):
    if not isinstance(field, BoundField):
        return str(field)

    css_class = 'form-control'
    if field.errors:
        css_class += ' is-invalid'
    else:
        css_class += ' is-valid'

    return f"""
    <div class="mb-3">
        <label for="{field.id_for_label}" class="form-label">{field.label}</label>
        {field.as_widget(attrs={'class': css_class})}
        <div class="invalid-feedback">{field.errors.as_text()}</div>
    </div>
    """
