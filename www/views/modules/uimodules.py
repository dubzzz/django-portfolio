from tornado.web import UIModule

class BootstrapForm(UIModule):
    def render(self, form, prefix="input"):
        r"""Shaping a form"""
        return self.render_string("form_bootstrap.html", form=form, prefix=prefix)

