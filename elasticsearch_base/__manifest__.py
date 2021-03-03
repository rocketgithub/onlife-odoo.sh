# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Elasticsearch Base",
    'summary': """
        Provides base module for Elasticsearch-ing Odoo records.""",

    'description': """
        Odoo Elasticsearch
    """,

    'author': "PyBrains",
    'email': "dev@pybrains.com",
    'website': "http://www.pybrains.com",
    'category': 'Base',
    'version': '13.0.1.1',

    'depends': [
        'base',
        'base_automation',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'wizard/index_management_wizard_view.xml',
        'views/menu_views.xml',
        'views/es_index_views.xml',
        'views/res_config_settings_views.xml',
    ],
}
