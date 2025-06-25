from django import template

register = template.Library()


@register.filter
def calc_order_total(items):
    return sum(item.price * item.quantity for item in items)


@register.filter
def mul(value, arg):
    return value * arg
