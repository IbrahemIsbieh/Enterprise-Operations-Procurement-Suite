from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EopsProcurementTender(models.Model):
    _inherit = 'eops.procurement.tender'

    vendor_bill_count = fields.Integer(
        string='Vendor Bills',
        compute='_compute_vendor_bill_data',
    )

    vendor_bill_total = fields.Monetary(
        string='Total Vendor Bills',
        currency_field='currency_id',
        compute='_compute_vendor_bill_data',
    )

    vendor_bill_residual = fields.Monetary(
        string='Outstanding Amount',
        currency_field='currency_id',
        compute='_compute_vendor_bill_data',
    )

    vendor_bill_ids = fields.Many2many(
        'account.move',
        string='Related Vendor Bills',
        compute='_compute_vendor_bill_data',
    )

    @api.depends(
        'selected_purchase_order_id',
        'selected_purchase_order_id.invoice_ids',
        'selected_purchase_order_id.invoice_ids.state',
        'selected_purchase_order_id.invoice_ids.move_type',
        'selected_purchase_order_id.invoice_ids.amount_total',
        'selected_purchase_order_id.invoice_ids.amount_residual',
    )
    def _compute_vendor_bill_data(self):
        for tender in self:
            purchase_order = tender.selected_purchase_order_id

            if purchase_order:
                bills = purchase_order.invoice_ids.filtered(
                    lambda move: move.move_type == 'in_invoice'
                )
            else:
                bills = self.env['account.move']

            tender.vendor_bill_ids = bills
            tender.vendor_bill_count = len(bills)

            posted_bills = bills.filtered(
                lambda move: move.state == 'posted'
            )

            tender.vendor_bill_total = sum(
                posted_bills.mapped('amount_total')
            )

            tender.vendor_bill_residual = sum(
                posted_bills.mapped('amount_residual')
            )

    def action_view_vendor_bills(self):
        self.ensure_one()

        if not self.selected_purchase_order_id:
            raise UserError(
                _('There is no selected purchase order for this tender.')
            )

        bills = self.selected_purchase_order_id.invoice_ids.filtered(
            lambda move: move.move_type == 'in_invoice'
        )

        if not bills:
            raise UserError(
                _(
                    'No vendor bills are linked to this purchase order yet. '
                    'Open the purchase order and create a vendor bill first.'
                )
            )

        if len(bills) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Vendor Bill'),
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': bills.id,
                'target': 'current',
            }

        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bills'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', bills.ids)],
            'context': {
                'default_move_type': 'in_invoice',
            },
            'target': 'current',
        }