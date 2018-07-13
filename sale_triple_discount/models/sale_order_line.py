# -*- coding: utf-8 -*-
# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2017 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_final_discount(self):
        self.ensure_one()
        if self.discounting_type == "additive":
            return self._additive_discount()
        elif self.discounting_type == "multiplicative":
            return self._multiplicative_discount()

    def _additive_discount(self):
        self.ensure_one()
        discounts = [getattr(self, x) or 0.0 for x in self._discount_fields()]
        return 1 - sum(discounts) / 100

    def _multiplicative_discount(self):
        self.ensure_one()
        discounts = [1 - (getattr(self, x) or 0.0) / 100
                     for x in self._discount_fields()]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return final_discount

    def _discount_fields(self):
        return ['discount', 'discount2', 'discount3']

    @api.depends('discount2', 'discount3')
    def _compute_amount(self):
        # updating the values of fields in the compute, that is compute is
        # depending on can lead to unexpected results, such as recomputation of
        # the fields once more returning a wrong value
        super(SaleOrderLine, self)._compute_amount()
        for line in self:
            prev_price_unit = line.price_unit
            price = prev_price_unit * line._get_final_discount()
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id
            )
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    discount2 = fields.Float(
        'Disc. 2 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )
    discount3 = fields.Float(
        'Disc. 3 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )
    discounting_type = fields.Selection(
        string="Discounting type",
        selection=[
            ('additive', 'Additive'),
            ('multiplicative', 'Multiplicative'),
        ],
        default="multiplicative",
        help="""Specifies whether discounts should be added additively
        of multiplicatively."""
    )

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Discount 2 must be lower than 100%.'),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         'Discount 3 must be lower than 100%.'),
    ]

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'discount2': self.discount2,
            'discount3': self.discount3,
        })
        return res

    @api.depends('discount2', 'discount3')
    def _get_price_reduce(self):
        # with introduction of additive discounts we need to change the way
        # discount is computed
        super(SaleOrderLine, self)._get_price_reduce()
        for line in self:
                line.price_reduce = (line.price_unit *
                                     line._get_final_discount())
