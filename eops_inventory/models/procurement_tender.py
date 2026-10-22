from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EopsProcurementTender(models.Model):
    _inherit = 'eops.procurement.tender'

    selected_purchase_order_state = fields.Selection(
        related='selected_purchase_order_id.state',
        string='Purchase Order Status',
        readonly=True,
    )

    stock_picking_ids = fields.Many2many(
        'stock.picking',
        string='Stock Receipts',
        compute='_compute_stock_pickings',
    )

    stock_picking_count = fields.Integer(
        string='Receipt Count',
        compute='_compute_stock_pickings',
    )

    @api.depends(
        'selected_purchase_order_id',
        'selected_purchase_order_id.picking_ids',
    )
    def _compute_stock_pickings(self):
        for tender in self:
            purchase_order = tender.selected_purchase_order_id

            if purchase_order:
                pickings = purchase_order.picking_ids
            else:
                pickings = self.env['stock.picking']

            tender.stock_picking_ids = pickings
            tender.stock_picking_count = len(pickings)

    def action_confirm_selected_purchase_order(self):
        self.ensure_one()
        self._check_manager()

        if self.state != 'awarded':
            raise UserError(
                _('You can only confirm the purchase order of an awarded tender.')
            )

        purchase_order = self.selected_purchase_order_id

        if not purchase_order:
            raise UserError(
                _('There is no purchase order linked to the selected supplier.')
            )

        if purchase_order.state == 'cancel':
            raise UserError(
                _('The selected purchase order has been cancelled.')
            )

        if purchase_order.state in ('purchase', 'done'):
            raise UserError(
                _('The selected purchase order has already been confirmed.')
            )

        if purchase_order.state == 'to approve':
            return {
                'type': 'ir.actions.act_window',
                'name': _('Purchase Order Approval'),
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_order.id,
                'target': 'current',
            }

        purchase_order.button_confirm()

        if purchase_order.state == 'to approve':
            return {
                'type': 'ir.actions.act_window',
                'name': _('Purchase Order Approval'),
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_order.id,
                'target': 'current',
            }

        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirmed Purchase Order'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': purchase_order.id,
            'target': 'current',
        }

    def action_view_stock_receipts(self):
        self.ensure_one()

        if not self.selected_purchase_order_id:
            raise UserError(
                _('Select a supplier with a linked purchase order first.')
            )

        pickings = self.selected_purchase_order_id.picking_ids

        if not pickings:
            raise UserError(
                _(
                    'No stock receipts are available yet. '
                    'Confirm the purchase order first and check its approval status.'
                )
            )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Receipts'),
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('id', 'in', pickings.ids)],
            'context': {
                'create': False,
            },
        }