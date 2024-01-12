from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg): 
    #value will be the value to which we will attach |.
    #name will be name of filter that will come after |split.
    #arg will be the actual manipulation that we want to perform, which is .split(',')
    #the filter will look like - " value|split:',' "
    return value.split(arg)
