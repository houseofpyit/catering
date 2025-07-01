from odoo import http
from odoo.http import request


class EasyLanguageSelector(http.Controller):

    @http.route('/get_idle_time/timer', auth='public', type='json')
    def get_idle_time(self):
        """
        Summery:
            Getting value that selected from the login user account and pass it to the js function.
        return:
            type:It is a variable, that contain selected minutes.
        """
        # if request.env.user.enable_idle:
        #     return request.env.user.idle_time
        return 60
