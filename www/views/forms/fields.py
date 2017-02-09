class Field(object):
    def __init__(self, field_type, field_name, label, help_text, required):
        self.field_type = field_type
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
                self.errors.append("Please fill input field: '%s'" % (self.field_name,))
                return None
            return ""
    
    def __str__(self):
        required_tag = "required" if self.required else ""
        return '<input type="%s" name="%s" %s>' % (self.field_type, self.field_name, required_tag,)

class TextField(Field):
    def __init__(self, field_name, label, help_text="", required=False):
        super(TextField, self).__init__("text", field_name, label, help_text, required)

class PasswordField(Field):
    def __init__(self, field_name, label, help_text="", required=False):
        super(PasswordField, self).__init__("password", field_name, label, help_text, required)

