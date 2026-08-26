from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_with_page(context, page_param, page_value):
    request = context["request"]
    query_dict = request.GET.copy()
    query_dict[page_param] = page_value
    return query_dict.urlencode()
