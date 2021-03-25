# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_price = fields.Float("Default Price", digits='Product Price', default=0.0)
