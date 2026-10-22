from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EopsPurchaseRequestLine(models.Model):
    _name = 'eops.purchase.request.line'
    _description = 'Purchase Request Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        default=10,
    )
    request_id = fields.Many2one(
        'eops.purchase.request',
        string='Purchase Request',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='restrict',
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
    )
    price_unit = fields.Float(
        string='Estimated Unit Price',
        required=True,
        default=0.0,
        digits='Product Price',
    )
    currency_id = fields.Many2one(
        related='request_id.currency_id',
        store=True,
        readonly=True,
    )
    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.description = (
                    line.product_id.display_name
                )
                line.product_uom_id = (
                    line.product_id.uom_id
                )
                line.price_unit = (
                    line.product_id.standard_price
                )

    @api.constrains('quantity', 'price_unit')
    def _check_quantity_and_price(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    'The requested quantity must be greater than zero.'
                )
            if line.price_unit < 0:
                raise ValidationError(
                    'The estimated unit price cannot be negative.'
                )