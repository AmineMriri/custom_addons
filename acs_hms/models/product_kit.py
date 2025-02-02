# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ACSMedicamentGroup(models.Model):
    _name = 'acs.product.kit'
    _order = 'sequence asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Kit"

    name = fields.Char(string='Group Name', required=True, tracking=True)
    sequence = fields.Integer(default=100)
    acs_kit_line_ids = fields.One2many('acs.product.kit.line', 'acs_kit_id', string='Kit lines')
    description = fields.Text("Description")


class ACSProductKitLine(models.Model):
    _name = 'acs.product.kit.line'
    _order = 'sequence asc'
    _description = "Product Kit Line"

    @api.depends('product_id','product_qty','unit_price', 'standard_price')
    def _get_total_price(self):
        for rec in self:
            rec.total_price = rec.unit_price * rec.product_qty
            rec.total_standard_price = rec.standard_price * rec.product_qty

    sequence = fields.Integer(default=100)
    acs_kit_id = fields.Many2one('acs.product.kit', string='Kit')
    product_template_id = fields.Many2one('product.template', string='Kit Product')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(related='product_id.name', readonly="1")
    uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure", readonly="1")
    product_qty = fields.Float(string='Quantity', required=True, default=1.0)
    unit_price = fields.Float(related='product_id.list_price', string='Product Price')
    standard_price = fields.Float(related='product_id.standard_price', string='Cost Price')
    total_price = fields.Float(compute=_get_total_price, string='Total Price')
    total_standard_price = fields.Float(compute=_get_total_price, string='Total Cost Price')

    def write(self, values):
        res = super(ACSProductKitLine, self).write(values)
        self.mapped('product_template_id').acs_update_price_for_kit()
        return res

    @api.model
    def create(self, values):
        res = super(ACSProductKitLine, self).create(values)
        res.product_template_id.acs_update_price_for_kit()
        return res

    def unlink(self):
        product_template_ids = self.mapped('product_template_id')
        res = super(ACSProductKitLine, self).unlink()
        product_template_ids.acs_update_price_for_kit()
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('acs_kit_line_ids','is_kit_product','acs_kit_line_ids.total_price')
    def acs_get_kit_amount_total(self):
        for rec in self:
            rec.kit_amount_total = sum(rec.acs_kit_line_ids.mapped('total_price'))
            rec.kit_cost_total = sum(rec.acs_kit_line_ids.mapped('total_standard_price'))

    is_kit_product = fields.Boolean("Kit Product", help="Adding this product will lead to component consumption when added in medical flow")
    acs_kit_line_ids = fields.One2many('acs.product.kit.line', 'product_template_id', string='Kit Components')
    kit_amount_total = fields.Float(compute='acs_get_kit_amount_total', string="Kit Total")
    kit_cost_total = fields.Float(compute='acs_get_kit_amount_total', string="Kit Cost Total")

    @api.onchange('is_kit_product')
    def onchange_is_kit_product(self):
        if self.is_kit_product:
            self.type = 'consu'

    def acs_update_price_for_kit(self):
        for rec in self:
            rec.list_price = rec.kit_amount_total
            rec.standard_price = rec.kit_cost_total

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: