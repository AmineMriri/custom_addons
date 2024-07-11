# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT


def float_to_time(hours):
    """ Convert a number of hours into a time object. """
    if hours == 24.0:
        return time.max
    fractional, integral = math.modf(hours)
    int_fractional = int(float_round(60 * fractional, precision_digits=0))
    if int_fractional > 59:
        integral += 1
        int_fractional = 0
    return time(int(integral), int_fractional, 0)


class Appointment(models.Model):
    _inherit = 'hms.appointment'

    # @api.depends('date')
    # def _get_schedule_date(self):
    #     for rec in self:
    #         rec.schedule_date = rec.date.date()

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}
    schedule_date = fields.Date(string='Schedule Date', states=READONLY_STATES)
    schedule_slot_id = fields.Many2one('appointment.schedule.slot.lines', string = 'Schedule Slot', states=READONLY_STATES)
    booked_online = fields.Boolean('Booked Online', states=READONLY_STATES)

    @api.model
    def clear_appointment_cron(self):
        if self.env.user.company_id.allowed_booking_payment:
            appointments = self.search([('booked_online','=', True),('state','=','draft')])
            for appointment in appointments:
                #cancel appointment after 20 minute if not paid
                create_time = appointment.create_date + timedelta(minutes=20)
                if create_time <= datetime.now():
                    if appointment.invoice_id:
                        if appointment.invoice_id.state=='paid':
                            continue
                        appointment.invoice_id.action_invoice_cancel()
                    appointment.appointment_cancel()

    #To Avoid code duplication in mobile api.
    def get_slot_data(self, physician_id, department_id, date=False, schedule_type="appointment"):
        if date:
            domain = [('slot_id.slot_date','=', date),('rem_limit','>=',1)]
        else:
            last_date = fields.Date.today() + timedelta(days=self.env.user.sudo().company_id.allowed_booking_online_days)
            domain = [('rem_limit','>=',1),('slot_id.slot_date','>=',fields.Date.today()),('slot_id.slot_date','<=',last_date)]

        if physician_id:
            domain += [('physician_id', '=', int(physician_id))]
        if department_id:
            domain += [('department_id', '=', int(department_id))]

        domain += [('slot_id.schedule_id.schedule_type', '=', schedule_type)]
        slot_lines = self.env['appointment.schedule.slot.lines'].sudo().search(domain)
        slot_data = []
        for slot in slot_lines:
            slot_data.append({
                'date': slot.slot_id.slot_date,
                'name': slot.name,
                'id': slot.id,
                'physician_id': slot.physician_id.id,
                'physician_name': slot.physician_id and slot.physician_id.name or '',
                'fees': slot.slot_id.schedule_id.appointment_price,
                'show_fees': slot.slot_id.schedule_id.show_fee_on_booking,
            })
        return slot_data

    @api.onchange('schedule_slot_id')
    def onchange_schedule_slot_id(self):
        if self.schedule_slot_id:
            self.date = self.schedule_slot_id.from_slot
            self.date_to = self.schedule_slot_id.to_slot

    @api.onchange('schedule_date')
    def onchange_schedule_date(self):
        self.schedule_slot_id = False

    def action_cancel(self):
        res = super(Appointment, self).action_cancel()
        self.schedule_slot_id = False
        return res


class HrDepartment(models.Model):
    _inherit = "hr.department"

    allowed_online_booking = fields.Boolean("Allowed Online Booking")
    basic_info = fields.Char("Basic Info", help="Publish on Website")
    image = fields.Binary(string='Image')
    allow_home_appointment = fields.Boolean("Allowed Home Visit Booking")
    show_fee_on_booking = fields.Boolean("Show Fees")


class HmsPhysician(models.Model):
    _inherit = "hms.physician"

    allowed_online_booking = fields.Boolean("Allowed Online Booking")
    basic_info = fields.Char("Basic Info", help="Publish on Website")
    allow_home_appointment = fields.Boolean("Allowed Home Visit Booking")
    show_fee_on_booking = fields.Boolean("Show Fees")
