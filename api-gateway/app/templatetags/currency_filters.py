from django import template

register = template.Library()

@register.filter(name='vnd')
def vnd(value):
    try:
        # Convert to float then int to drop decimals
        integer_value = int(float(value))
        # Format with comma separator then replace with dot for VN locale
        formatted = f"{integer_value:,}".replace(",", ".")
        return formatted
    except (ValueError, TypeError):
        return value
