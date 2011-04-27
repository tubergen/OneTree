'''
adapted and modified code from: http://www.soyoucode.com/2011/set-variable-django-template
'''

from django import template
 
register = template.Library()
 
class SetVarNode(template.Node):
 
    def __init__(self, var_name, var_action, var_value):
        self.var_name = var_name
        self.var_value = var_value
        self.var_action = var_action
 
    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        if self.var_action == '+=':
            context[self.var_name] += value
        else:
            context[self.var_name] = value
        return u""
 
def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
        {% set <var_name> += <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %} or {% set <var_name> += <var_value> %}")
    return SetVarNode(parts[1], parts[2], parts[3])
 
register.tag('set', set_var)
