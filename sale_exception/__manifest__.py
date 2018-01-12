# -*- coding: utf-8 -*-
# Copyright 2011 Akretion, Camptocamp, Sodexis
# Copyright 2017 Akretion, Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Sale Exception',
 'summary': 'Custom exceptions on sale order',
 'version': '11.0.1.0.0',
 'category': 'Generic Modules/Sale',
 'author': "Akretion, Sodexis, Camptocamp, Odoo Community Association (OCA)",
 'website': 'http://www.akretion.com',
 'depends': ['sale', 'base_exception'],
 'license': 'AGPL-3',
 'data': [
     'data/sale_exception_data.xml',
     'wizard/sale_exception_confirm_view.xml',
     'views/sale_view.xml',
 ],
 }
