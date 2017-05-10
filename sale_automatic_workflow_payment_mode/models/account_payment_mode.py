# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, api, _

from odoo.exceptions import UserError


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    workflow_process_id = fields.Many2one(
        comodel_name='sale.workflow.process',
        string='Automatic Workflow'
    )

    @api.onchange("bank_account_link","workflow_process_id")
    def check_journal(self):
        if self.bank_account_link != 'fixed' and self.workflow_process_id:
            self.workflow_process_id = False
            message={ 'title': _('Attention please'),
                        'message' : _('To use sale automatic workflow the link to bank account must be fixed')}
            return {'warning': message}

