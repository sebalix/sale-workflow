# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, models, fields, _
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(default='to_approve')

    @api.model
    def _setup_fields(self):
        super(SaleOrder, self)._setup_fields()
        selection = self._fields['state'].selection
        exists = False
        for idx, (state, __) in enumerate(selection):
            if state == 'to_approve':
                exists = True
        if not exists:
            selection.insert(0, ('to_approve', _('To Approve')))
        for act_field in self._fields.values():

            if act_field.states and all(
                x in act_field.states.keys() for x in ['draft', 'sent']
            ):
                act_field.states = {'to_approve': [('readonly', False)]}

    @api.multi
    def is_amount_to_approve(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency.compute(limit_amount, self.currency_id)
        return float_compare(
            limit_amount, self.amount_total,
            precision_rounding=self.currency_id.rounding) <= 0

    @api.multi
    def is_to_approve(self):
        self.ensure_one()
        return (self.company_id.so_double_validation == 'two_step' and
                self.is_amount_to_approve() and
                not self.user_has_groups('sales_team.group_sale_manager'))

    @api.model
    def create(self, vals):
        obj = super().create(vals)
        if not obj.is_to_approve():
            obj.state = 'draft'
        return obj

    @api.multi
    def action_approve(self):
        self.write({'state': 'draft'})

    @api.multi
    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in (
                'to_approve',
                'draft',
                'sent',
                'cancel'
            ) else _('Sales Order')
