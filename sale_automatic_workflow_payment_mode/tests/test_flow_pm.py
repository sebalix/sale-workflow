# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import common
from odoo.addons.sale_automatic_workflow.tests.test_flow import TestAutomaticWorkflow


class TestAutomaticWorkflowPaymentMode(TestAutomaticWorkflow):

    def _create_sale_order(self, workflow, override=None):
        new_order = super(TestAutomaticWorkflowPaymentMode, self).\
            _create_sale_order(workflow, override)
        self.pay_method = self.env['account.payment.method'].create({
            'name': 'default inbound',
            'code': 'definb',
            'payment_type':'inbound'})
        self.acc_journ = self.env['account.journal'].create({
            'name': 'Bank US',
            'type': 'bank',
            'code': 'BNK68',})
        #    'currency_id': self.env.ref("base.USD").id})
        self.pay_mode = self.env['account.payment.mode'].create({
            'name': "Julius Caesare payment",
            'bank_account_link':'fixed',
            'fixed_journal_id':self.acc_journ.id,
            'payment_method_id':self.pay_method.id,
            'workflow_process_id':workflow.id})
        new_order.payment_mode_id=self.pay_mode
        new_order.payment_mode_id.workflow_process_id = new_order.workflow_process_id.id
        return new_order

    def _create_full_automatic(self, override=None):
        values = super(TestAutomaticWorkflowPaymentMode, self).\
            _create_full_automatic(override)
        reg_pay_dict={'register_payment':True}
        values.update(reg_pay_dict)
        return values

    def test_full_automatic(self):
        workflow = self._create_full_automatic()
        sale = self._create_sale_order(workflow)
        sale._onchange_workflow_process_id()
        sale.onchange_payment_mode_set_workflow()
        self.assertEqual(sale.state, 'draft')
        self.assertEqual(sale.workflow_process_id, workflow)
        self.progress()
        self.assertEqual(sale.state, 'sale')
        self.assertTrue(sale.picking_ids)
        self.assertTrue(sale.invoice_ids)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, 'open')
        picking = sale.picking_ids
        self.progress()
        self.assertEqual(picking.state, 'done')
        self.progress()
        self.assertEqual(invoice.state, 'paid')

    # def test_onchange(self):
    #     workflow = self._create_full_automatic()
    #     sale = self._create_sale_order(workflow)
    #     sale._onchange_workflow_process_id()
    #     sale.onchange_payment_mode_set_workflow()
    #     self.assertEqual(sale.picking_policy, 'one')
    #     workflow2 = self._create_full_automatic(
    #         override={
    #             'picking_policy': 'direct',
    #         }
    #     )
    #     sale.workflow_process_id = workflow2.id
    #     sale._onchange_workflow_process_id()
    #     self.assertEqual(sale.picking_policy, 'direct')
    #
    # def test_date_invoice_from_sale_order(self):
    #     workflow = self._create_full_automatic()
    #     # date_order on sale.order is date + time
    #     # date_invoice on account.invoice is date only
    #     last_week_time = datetime.now() - timedelta(days=7)
    #     last_week_time = fields.Datetime.to_string(last_week_time)
    #     last_week_date = last_week_time[:10]
    #     override = {
    #         'date_order': last_week_time,
    #     }
    #     sale = self._create_sale_order(workflow, override=override)
    #     sale._onchange_workflow_process_id()
    #     self.assertEqual(sale.date_order, last_week_time)
    #     self.progress()
    #     self.assertTrue(sale.invoice_ids)
    #     invoice = sale.invoice_ids
    #     self.assertEqual(invoice.date_invoice, last_week_date)
    #     self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)
    #
    # def test_invoice_from_picking_with_service_product(self):
    #     workflow = self._create_full_automatic()
    #     product_service = self.env.ref('product.service_order_01')
    #     product_uom_hour = self.env.ref('product.product_uom_hour')
    #     override = {
    #         'order_line': [(0, 0, {
    #             'name': 'Prepaid Consulting',
    #             'product_id': product_service.id,
    #             'product_uom_qty': 1,
    #             'product_uom': product_uom_hour.id,
    #         })],
    #     }
    #     sale = self._create_sale_order(workflow, override=override)
    #     sale._onchange_workflow_process_id()
    #     self.progress()
    #     self.assertFalse(sale.picking_ids)
    #     self.assertTrue(sale.invoice_ids)
    #     invoice = sale.invoice_ids
    #     self.assertEqual(invoice.workflow_process_id, sale.workflow_process_id)
    #
    # def test_journal_on_invoice(self):
    #     sale_journal = self.env['account.journal'].search(
    #         [('type', '=', 'sale')], limit=1)
    #     new_sale_journal = self.env['account.journal'].create({"name": "TTSA",
    #                                                            "code": "TTSA",
    #                                                            "type": "sale"})
    #     workflow = self._create_full_automatic()
    #     sale = self._create_sale_order(workflow)
    #     sale._onchange_workflow_process_id()
    #     self.progress()
    #     self.assertTrue(sale.invoice_ids)
    #     invoice = sale.invoice_ids
    #     self.assertEqual(invoice.journal_id.id, sale_journal.id)
    #
    #     workflow = self._create_full_automatic(
    #         override={'property_journal_id': new_sale_journal.id},
    #     )
    #     sale = self._create_sale_order(workflow)
    #     sale._onchange_workflow_process_id()
    #     self.progress()
    #     self.assertTrue(sale.invoice_ids)
    #     invoice = sale.invoice_ids
    #     self.assertEqual(invoice.journal_id.id, new_sale_journal.id)


