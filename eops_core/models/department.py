from odoo import fields, models


class EopsDepartment(models.Model):
    _name = 'eops.department'
    _description = 'Operations Department'
    _order = 'name, id'

    name = fields.Char(
        string='Department Name',
        required=True,
    )
    code = fields.Char(
        string='Department Code',
        required=True,
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Department Manager',
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

    _eops_department_code_company_unique = models.Constraint(
        'UNIQUE(code, company_id)',
        'The department code must be unique per company.',
    )
