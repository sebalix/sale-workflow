# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Credit Points',
    'version': '11.0.1.0.0',
    'category': 'Sales',
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com/',
    'depends': [
        'sale',
    ],
    'data': [
        'security/groups.xml',
        'data/res_currency.xml',
        'views/partner.xml',
        'wizards/manage_credit_point.xml',
    ],
}
