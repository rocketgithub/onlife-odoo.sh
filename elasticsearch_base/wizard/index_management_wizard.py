# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from odoo.tools.profiler import profile
# noinspection PyUnresolvedReferences
from odoo.addons.elasticsearch_base.tools import index
from odoo.exceptions import UserError

_logging = logging.getLogger(__name__)


class IndexManagementkWizard(models.TransientModel):
    _name = 'index.management.wizard'
    _description = "Index Management Wizard"

    name = fields.Char("Name", compute='_compute_name', store=True)
    index_ids = fields.Many2many('search.engine.index', string="Indexes")
    option = fields.Selection([
        ('create_all_indexes', "Create All Indexes"),
        ('create_relevant_indexes', "Create Relevant Indexes"),
        ('create_all_documents', "Create All Documents"),
        ('create_relevant_documents', "Create Relevant Documents"),
        ('update_all_documents', "Update All Documents"),
        ('update_relevant_documents', "Update Relevant Documents"),
        ('delete_relevant_indexes', "Delete Relevant Indexes")
    ], string="Option", required=True)

    @api.depends('create_date')
    def _compute_name(self):
        for rec in self:
            rec.name = "index-%s" % fields.Datetime.now()

    @profile
    def action_confirm(self):
        self.ensure_one()
        string = "self.%s()" % self.option
        _logging.info(string)
        return eval(string)

    @api.model
    def default_get(self, fields):
        res = super(IndexManagementkWizard, self).default_get(fields)
        res['index_ids'] = self._context and self._context.get('active_ids')
        return res

    def create_all_indexes(self):
        index.create_all_indexes(self)

    def create_relevant_indexes(self):
        index.create_relevant_indexes(self, self.index_ids)

    def delete_relevant_indexes(self):
        for index_id in self.index_ids:
            if index_id.index_exists:
                index.delete_relevant_indexes(self, index_id)
        self.index_ids.unlink()

    def create_all_documents(self):
        index.create_all_documents(self)

    def create_relevant_documents(self):
        index.create_relevant_documents(self, self.index_ids)

    def update_all_documents(self):
        index.update_all_documents()

    def update_relevant_documents(self):
        index.update_relevant_documents(self, self.index_ids)
