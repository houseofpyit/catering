import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class View(models.Model):
    _inherit = 'ir.ui.view'

    def _render_template(self, template, values=None, engine='ir.qweb'):
        if template in ['web.login', 'web.webclient_bootstrap']:
            if not values:
                values = {}
            values["title"] = "AMAZE"
        return super(View, self)._render_template(template, values=values, engine=engine)