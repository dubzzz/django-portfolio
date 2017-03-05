from tornado.escape import utf8, _unicode, xhtml_escape, url_escape

class AbstractField(object):
    def __init__(self, field_name, label, help_text, required):
        self.field_name = field_name
        self.label = label
        self.help_text = help_text
        self.required = required
        self.errors = list()
    
    def read(self, args):    
        try:
            return args[self.field_name][0].decode('utf_8')
        except (KeyError, IndexError) as e:
            if self.required:
                self.errors.append("Please fill field: '%s'" % (self.field_name,))
                return None
            return ""
    
class InputField(AbstractField):
    def __init__(self, field_type, field_name, label, help_text, required):
        super(InputField, self).__init__(field_name, label, help_text, required)
        self.field_type = field_type
    
    def render(self, attrs):
        attrs["type"] = self.field_type
        attrs["name"] = self.field_name
        if self.required:
            attrs["required"] = None
        return '<input %s>' % (" ".join(['%s="%s"' % (key, xhtml_escape(value)) if value is not None else key for key,value in attrs.items()]),)
        
    def __str__(self):
        return self.render({})

class BooleanField(InputField):
    def __init__(self, field_name, label, help_text="", required=False):
        super(BooleanField, self).__init__("checkbox", field_name, label, help_text, required)
        self._is_checked = False

    def withIsChecked(self, is_checked):
        self._is_checked = is_checked
        return self
    
    def __str__(self):
        attrs = {}
        if self._is_checked is True:
            attrs["checked"] = None
        return self.render(attrs)

class TextField(InputField):
    def __init__(self, field_name, label, help_text="", required=False):
        super(TextField, self).__init__("text", field_name, label, help_text, required)
        self._max_length = None
    
    def withMaxLength(self, max_length):
        self._max_length = max_length
        return self
    
    def read(self, args):
        out = super(TextField, self).read(args)
        if self._max_length != None and out is not None and len(out) >= self._max_length:
            if self.required:
               self.errors.append("Invalid value: '%s' is limited to %d characters" % (self.field_name, self._max_length))
               return None
            out = out[:self._max_length]
        return out
    
    def __str__(self):
        attrs = {}
        if self._max_length is not None:
            attrs["maxlength"] = str(self._max_length)
        return self.render(attrs)

class PasswordField(InputField):
    def __init__(self, field_name, label, help_text="", required=False):
        super(PasswordField, self).__init__("password", field_name, label, help_text, required)

class AbstractSelectField(AbstractField):
    def __init__(self, field_name, label, help_text, required):
        super(AbstractSelectField, self).__init__(field_name, label, help_text, required)
        self.choices = []
    
    def withChoices(self, choices):
        self.choices = choices #array of pair (tuple) { key: string, value: string }
        return self
        
    def render(self, attrs):
        out = list()
        
        attrs["name"] = self.field_name
        if self.required:
            attrs["required"] = None
        out.append('<select %s>' % (" ".join(['%s="%s"' % (key, xhtml_escape(value)) if value is not None else key for key,value in attrs.items()]),))
        
        for key, value in self.choices:
            out.append('<option value="%s">%s</option>' % (xhtml_escape(key), xhtml_escape(value),))
        out.append('</select>')
        return "".join(out)

class SelectField(AbstractSelectField):
    def __init__(self, field_name, label, help_text, required):
        super(SelectField, self).__init__(field_name, label, help_text, required)
    def __str__(self):
        return self.render({})

class MultiSelectField(AbstractSelectField):
    def __init__(self, field_name, label, help_text, required):
        super(MultiSelectField, self).__init__(field_name, label, help_text, required)
    def __str__(self):
        return self.render({'multiple': None})

