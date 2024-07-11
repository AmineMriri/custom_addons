# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class ResCompany(models.Model):
    _inherit = "res.company"

    birthday_mail_template_id = fields.Many2one('mail.template', 'Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.")
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient', help='Set this True if the Givernment Identity in patients should be unique.')

    #Call this method directly in case of dependcy issue like acs_certification (call in acs_hms_certification)
    def acs_create_sequence(self, name, code, prefix, padding=3):
        self.env['ir.sequence'].sudo().create({
            'name': self.name + " : " + name,
            'code': code,
            'padding': padding,
            'number_next': 1,
            'number_increment': 1,
            'prefix': prefix,
            'company_id': self.id,
            'acs_auto_create': False,
        })

    def acs_auto_create_sequences(self):
        sequences = self.env['ir.sequence'].search([('acs_auto_create','=',True)])
        for sequence in sequences:
            self.acs_create_sequence(name=sequence.name, code=sequence.code, prefix=sequence.prefix, padding=sequence.padding)

    #Auto create marked sequences in other HMS modules.
    @api.model
    def create(self, vals):
        rec = super(ResCompany, self).create(vals)
        rec.acs_auto_create_sequences()
        return rec


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    birthday_mail_template_id = fields.Many2one('mail.template', 
        related='company_id.birthday_mail_template_id',
        string='Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.", readonly=False)
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient',
         related='company_id.unique_gov_code', readonly=False,
         help='Set this True if the Givernment Identity in patients should be unique.')