from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EopsPurchaseRequest(models.Model):
    _name = 'eops.purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Request Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True,
    )
    requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    department_id = fields.Many2one(
        'eops.department',
        string='Department',
        ondelete='restrict',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )
    request_date = fields.Date(
        string='Request Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    required_date = fields.Date(
        string='Required Date',
        tracking=True,
    )
    reason = fields.Text(
        string='Request Reason',
        required=True,
    )
    line_ids = fields.One2many(
        'eops.purchase.request.line',
        'request_id',
        string='Request Lines',
        copy=True,
    )
    amount_total = fields.Monetary(
        string='Estimated Total',
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id',
    )
    approver_id = fields.Many2one(
        'res.users',
        string='Assigned Approver',
        readonly=True,
        copy=False,
        tracking=True,
    )
    approval_policy_id = fields.Many2one(
        'eops.approval.policy',
        string='Approval Policy',
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        required=True,
        default='draft',
        copy=False,
        tracking=True,
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        copy=False,
        tracking=True,
    )

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for request in self:
            request.amount_total = sum(
                request.line_ids.mapped('subtotal')
            )

    @api.constrains('request_date', 'required_date')
    def _check_dates(self):
        for request in self:
            if (
                request.request_date
                and request.required_date
                and request.required_date < request.request_date
            ):
                raise ValidationError(
                    'The required date cannot be earlier than '
                    'the request date.'
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'eops.purchase.request'
                    ) or 'New'
                )
        return super().create(vals_list)

    def _check_approver_access(self):
        if self.env.user.has_group(
            'eops_core.group_eops_manager'
        ):
            return

        for request in self:
            if request.approver_id != self.env.user:
                raise UserError(
                    _('Only the assigned approver or an Operations '
                      'Manager can perform this action.')
                )

    def action_submit(self):
        for request in self:
            if request.state != 'draft':
                raise UserError(
                    _('Only draft requests can be submitted.')
                )

            if not request.line_ids:
                raise UserError(
                    _('Add at least one product before submitting.')
                )

            policy = self.env['eops.approval.policy'].search(
                [
                    ('active', '=', True),
                    ('company_id', '=', request.company_id.id),
                    ('currency_id', '=', request.currency_id.id),
                    ('minimum_amount', '<=', request.amount_total),
                    ('maximum_amount', '>=', request.amount_total),
                ],
                order='sequence, id',
                limit=1,
            )

            if not policy:
                raise UserError(
                    _('No active approval policy matches this request '
                      'amount, company, and currency.')
                )

            request.write({
                'state': 'submitted',
                'approver_id': policy.approver_id.id,
                'approval_policy_id': policy.id,
                'rejection_reason': False,
            })

            request.message_post(
                body=_('Purchase request submitted for approval.')
            )

        return True

    def action_approve(self):
        self._check_approver_access()

        for request in self:
            if request.state != 'submitted':
                raise UserError(
                    _('Only submitted requests can be approved.')
                )

            request.write({
                'state': 'approved',
                'rejection_reason': False,
            })

            request.message_post(
                body=_('Purchase request approved.')
            )

        return True

    def action_reject(self):
        self._check_approver_access()

        for request in self:
            if request.state != 'submitted':
                raise UserError(
                    _('Only submitted requests can be rejected.')
                )

            request.write({
                'state': 'rejected',
                'rejection_reason': False,
            })

            request.message_post(
                body=_('Purchase request rejected.')
            )

        return True

    def action_reset_to_draft(self):
        if not self.env.user.has_group(
            'eops_core.group_eops_manager'
        ):
            raise UserError(
                _('Only an Operations Manager can reset a request.')
            )

        for request in self:
            if request.state not in ('rejected', 'cancelled'):
                raise UserError(
                    _('Only rejected or cancelled requests can '
                      'be reset to draft.')
                )

            request.write({
                'state': 'draft',
                'approver_id': False,
                'approval_policy_id': False,
                'rejection_reason': False,
            })

        return True

    def action_cancel(self):
        for request in self:
            if request.state not in ('draft', 'submitted'):
                raise UserError(
                    _('Only draft or submitted requests can be cancelled.')
                )

            if (
                request.state == 'submitted'
                and request.requester_id != self.env.user
                and not self.env.user.has_group(
                    'eops_core.group_eops_manager'
                )
            ):
                raise UserError(
                    _('Only the requester or an Operations Manager '
                      'can cancel a submitted request.')
                )

            request.write({
                'state': 'cancelled',
            })

        return True