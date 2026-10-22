from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EopsApprovalPolicy(models.Model):
    _name = 'eops.approval.policy'
    _description = 'Purchase Approval Policy'
    _order = 'sequence, id'

    name = fields.Char(
        string='Policy Name',
        required=True,
    )
    sequence = fields.Integer(
        default=10,
    )
    minimum_amount = fields.Monetary(
        string='Minimum Amount',
        required=True,
        default=0.0,
    )
    maximum_amount = fields.Monetary(
        string='Maximum Amount',
        required=True,
        default=1000000.0,
    )
    currency_id = fields.Many2one(
        'res.currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True,
        ondelete='restrict',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        default=True,
    )

    @api.constrains('minimum_amount', 'maximum_amount')
    def _check_amount_range(self):
        for record in self:
            if record.minimum_amount < 0:
                raise ValidationError(
                    'The minimum amount cannot be negative.'
                )
            if record.maximum_amount < record.minimum_amount:
                raise ValidationError(
                    'The maximum amount must be greater than '
                    'or equal to the minimum amount.'
                )