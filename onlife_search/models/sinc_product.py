# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SincProduct(models.AbstractModel):
    _inherit = 'sinc_bigcommerce.product'

    def campos(self):
        res = super(SincProduct, self).campos()
        clasicos = res.get('clasicos')
        clasicos.remove(['list_price', 'sale_price'])
        clasicos.append(['default_price', 'sale_price'])
        return res.update({'clasicos': clasicos})
