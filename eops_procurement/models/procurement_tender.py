from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EopsProcurementTender(models.Model):
    _name = 'eops.procurement.tender'
    _description = 'Procurement Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Tender Reference',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        tracking=True,
    )
    purchase_request_id = fields.Many2one(
        'eops.purchase.request',
        string='Purchase Request',
        required=True,
        ondelete='restrict',
        tracking=True,
        check_company=True,
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
        related='purchase_request_id.currency_id',
        store=True,
        readonly=True,
    )
    vendor_line_ids = fields.One2many(
        'eops.procurement.tender.vendor',
        'tender_id',
        string='Supplier Quotations',
        copy=False,
    )
    selected_vendor_line_id = fields.Many2one(
        'eops.procurement.tender.vendor',
        string='Selected Supplier',
        compute='_compute_selected_vendor',
        store=True,
    )
    selected_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Selected Purchase Order',
        related='selected_vendor_line_id.purchase_order_id',
        readonly=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('rfqs_created', 'RFQs Created'),
            ('awarded', 'Awarded'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
    )
    notes = fields.Text(string='Notes')

    @api.depends(
        'vendor_line_ids.is_selected',
        'vendor_line_ids.purchase_order_id',
    )
    def _compute_selected_vendor(self):
        for tender in self:
            selected_lines = tender.vendor_line_ids.filtered(
                lambda line: line.is_selected
            )
            tender.selected_vendor_line_id = (
                selected_lines[:1] if len(selected_lines) == 1 else False
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'eops.procurement.tender'
                    ) or 'New'
                )
        return super().create(vals_list)

    @api.constrains('purchase_request_id', 'company_id')
    def _check_request_company(self):
        for tender in self:
            if (
                tender.purchase_request_id
                and tender.company_id
                != tender.purchase_request_id.company_id
            ):
                raise ValidationError(
                    _('The tender and purchase request must belong to the same company.')
                )

    def _check_manager(self):
        if not self.env.user.has_group(
            'eops_core.group_eops_manager'
        ):
            raise UserError(
                _('Only an Operations Manager can perform this action.')
            )

    def action_create_rfqs(self):
        self.ensure_one()
        self._check_manager()

        if self.state != 'draft':
            raise UserError(
                _('RFQs can only be created for a draft tender.')
            )

        request = self.purchase_request_id

        if request.state != 'approved':
            raise UserError(
                _('The linked purchase request must be approved first.')
            )

        if not request.line_ids:
            raise UserError(
                _('The purchase request has no product lines.')
            )

        if not self.vendor_line_ids:
            raise UserError(
                _('Add at least one supplier before creating RFQs.')
            )

        if len(self.vendor_line_ids.mapped('vendor_id')) != len(
            self.vendor_line_ids
        ):
            raise UserError(
                _('Each supplier can only be added once to a tender.')
            )

        for vendor_line in self.vendor_line_ids:
            if vendor_line.purchase_order_id:
                raise UserError(
                    _('An RFQ already exists for supplier %s.')
                    % vendor_line.vendor_id.display_name
                )

        for vendor_line in self.vendor_line_ids:
            order_lines = []

            for request_line in request.line_ids:
                order_lines.append((0, 0, {
                    'product_id': request_line.product_id.id,
                    'name': request_line.description,
                    'product_qty': request_line.quantity,
                    'product_uom_id': request_line.product_uom_id.id,
                    'price_unit': request_line.price_unit,
                    'date_planned': fields.Datetime.now(),
                }))

            purchase_order = self.env['purchase.order'].create({
                'partner_id': vendor_line.vendor_id.id,
                'company_id': self.company_id.id,
                'origin': '%s / %s' % (request.name, self.name),
                'order_line': order_lines,
            })

            vendor_line.write({
                'purchase_order_id': purchase_order.id,
            })

        self.write({'state': 'rfqs_created'})
        self.message_post(
            body=_('Supplier RFQs have been created.')
        )
        return True

    def action_award_tender(self):
        self.ensure_one()
        self._check_manager()

        if self.state != 'rfqs_created':
            raise UserError(
                _('Only tenders with created RFQs can be awarded.')
            )

        selected_lines = self.vendor_line_ids.filtered(
            lambda line: line.is_selected
        )

        if len(selected_lines) != 1:
            raise UserError(
                _('Select exactly one supplier quotation before awarding the tender.')
            )

        selected_line = selected_lines[0]

        if not selected_line.purchase_order_id:
            raise UserError(
                _('The selected supplier does not have an RFQ.')
            )

        self.write({'state': 'awarded'})
        self.message_post(
            body=_('Tender awarded to %s.')
            % selected_line.vendor_id.display_name
        )
        return True

    def action_cancel(self):
        self.ensure_one()
        self._check_manager()

        if self.state == 'awarded':
            raise UserError(
                _('An awarded tender cannot be cancelled.')
            )

        if self.state == 'cancelled':
            raise UserError(
                _('This tender is already cancelled.')
            )

        self.write({'state': 'cancelled'})
        self.message_post(body=_('Tender cancelled.'))
        return True

    def action_reset_to_draft(self):
        self.ensure_one()
        self._check_manager()

        if self.state != 'cancelled':
            raise UserError(
                _('Only cancelled tenders can be reset to draft.')
            )

        if self.vendor_line_ids.filtered(
            lambda line: line.purchase_order_id
        ):
            raise UserError(
                _('Remove or resolve existing RFQs before resetting this tender.')
            )

        self.write({'state': 'draft'})
        return True

    def action_view_selected_purchase_order(self):
        self.ensure_one()

        if not self.selected_purchase_order_id:
            raise UserError(
                _('No supplier quotation has been selected.')
            )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Selected Purchase Order'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.selected_purchase_order_id.id,
            'target': 'current',
        }


class EopsProcurementTenderVendor(models.Model):
    _name = 'eops.procurement.tender.vendor'
    _description = 'Procurement Tender Supplier'
    _order = 'id'

    tender_id = fields.Many2one(
        'eops.procurement.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        index=True,
    )

    company_id = fields.Many2one(
        'res.company',
        related='tender_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )

    vendor_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        ondelete='restrict',
        check_company=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='RFQ / Purchase Order',
        readonly=True,
        copy=False,
        ondelete='restrict',
        check_company=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='tender_id.currency_id',
        readonly=True,
    )
    amount_total = fields.Monetary(
        string='Quotation Total',
        related='purchase_order_id.amount_total',
        currency_field='currency_id',
        readonly=True,
    )
    is_selected = fields.Boolean(
        string='Select as Winner',
        default=False,
    )

    @api.constrains('tender_id', 'vendor_id')
    def _check_unique_vendor(self):
        for line in self:
            if line.tender_id and line.vendor_id:
                duplicate = self.search_count([
                    ('id', '!=', line.id),
                    ('tender_id', '=', line.tender_id.id),
                    ('vendor_id', '=', line.vendor_id.id),
                ])
                if duplicate:
                    raise ValidationError(
                        _('A supplier can only be added once to a tender.')
                    )

    @api.constrains('is_selected', 'tender_id')
    def _check_selected_vendor(self):
        for line in self:
            if line.is_selected and line.tender_id.state == 'awarded':
                selected_lines = line.tender_id.vendor_line_ids.filtered(
                    lambda vendor_line: vendor_line.is_selected
                )
                if len(selected_lines) != 1:
                    raise ValidationError(
                        _('An awarded tender must have exactly one selected supplier.')
                    )
