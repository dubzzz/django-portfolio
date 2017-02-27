from fields import BooleanField, TextField, PasswordField

class AbstractForm(object):
    def __init__(self, fields):
        self.fields = fields
        self.error = False
        self.errors = list()
    
    def read(self, handler):
        args = handler.request.arguments
        query_params = dict()
        for f in self.fields:
            param = f.read(args)
            if param is None:
                self.error = True
            else:
                query_params[f.field_name] = param
        return query_params

class LoginForm(AbstractForm):
    def __init__(self):
        username = TextField("username", "Username", "Username", True)
        password = PasswordField("password", "Password", "Password", True)
        super(LoginForm, self).__init__([username, password])

class DummyForm(AbstractForm):
    def __init__(self):
        super(DummyForm, self).__init__([])

class ProjectHeaderForm(AbstractForm):
    def __init__(self):
        fields = [
                TextField("name", "Name", "Project name", True).withMaxLength(50)
                , TextField("name_url", "Name url", "Project name (URL)", True).withMaxLength(20)
                , TextField("short_description", "Short description", "Short description (max. 155)", True).withMaxLength(155)
                , TextField("year", "Year", "Release date", True)
                , BooleanField("private", "Private", "Private => visible only if logged in", True).withIsChecked(True)
        ]
        super(ProjectHeaderForm, self).__init__(fields)

