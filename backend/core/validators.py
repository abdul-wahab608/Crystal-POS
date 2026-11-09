from django.core.exceptions import ValidationError


def validate_unit_code(value):
    from .models import Unit

    if not Unit.objects.filter(code=value).exists():
        raise ValidationError(f"Unknown unit '{value}'. Add it under Units first.")
