# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class EsSearch(models.Model):
    _inherit = 'es.mixin'
    _name = 'es.search'
    _description = 'ES Search'

    @api.model
    def query(self, **kwargs):
        res = self.search_document(**kwargs)
        return res

    @api.model
    def count(self, **kwargs):
        res = self.search_count(**kwargs)
        return res
