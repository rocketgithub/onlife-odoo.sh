# noinspection PyStatementEffect
{
    # App information
    'name': "Fuzzy Search API for OnLife",
    'version': '13.0.1.19',
    'category': 'Inventory',
    'summary': """
Provides Fuzzy Search API for OnLife""",
    'license': 'OPL-1',
    'author': "PyBrains",
    'website': 'http://www.pybrains.com/',
    'maintainer': "PyBrains",

    # Dependencies
    'depends': [
        'base',
        'elasticsearch_base',
        'sinc_bigcommerce'
    ],

    # Views, Data, Templates, etc.
    'data': [
        'views/product_template.xml'
    ],

    'installable': True,
}
