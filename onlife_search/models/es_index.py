# -*- coding: utf-8 -*-

from odoo import models

default_model_domain = {'product.template': [('sinc_id', '>', 0)]}


class EsIndex(models.Model):
    _inherit = 'es.index'

    def get_model_domain(self):
        res = super(EsIndex, self).get_model_domain()
        res_fields = map(lambda x: x[0], res)
        default_domain = default_model_domain.get(self.model_name, [])
        for domain in default_domain:
            if domain[0] not in res_fields:
                res.extend(default_domain)
        return res
