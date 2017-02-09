from fields import TextField, PasswordField

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

