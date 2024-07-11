# -*- coding: utf-8 -*-

import time
import datetime
import pytz
from datetime import timedelta

from odoo import api, fields, models, http, _
from odoo.http import route, request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.website.controllers.main import Website
from odoo.fields import Command

from odoo.addons.payment.controllers import portal as payment_portal


class HMSWebsite(Website):

    #Appointment Booking
    def create_booking_data(self):
        user = request.env['res.users'].sudo().browse(request.uid)
        values = {
            'error': {},
            'error_message': []
        }

        department_ids = request.env['hr.department'].sudo().search([('patient_department','=',True),('allowed_online_booking','=',True)])
        physician_ids = request.env['hms.physician'].sudo().search([('allowed_online_booking','=',True)])

        values.update({
            'slots': [],
            'slot_lines': [],
            'partner': user.partner_id,
            'department_ids': department_ids,
            'physician_ids': physician_ids,
            'appointment_tz': False,
            'allow_department_selection': True if department_ids else False,
            'allow_physician_selection': True if physician_ids else False,
        })
        return values

    def user_booking_data(self, post):
        values = {
            'error': {},
            'error_message': []
        }
        physician_id = post.get('physician_id')
        department_id = post.get('department_id')
        appoitment_by = post.get('appoitment_by','physician')
        physician = department = ''
        allow_home_appointment = False
        
        if physician_id:
            physician = request.env['hms.physician'].sudo().search([('id','=',int(physician_id))])
            allow_home_appointment = physician.allow_home_appointment
        if department_id:
            department = request.env['hr.department'].sudo().search([('id','=',int(department_id))])
            allow_home_appointment = department.allow_home_appointment
        if appoitment_by=='physician':
            department = ''
        if appoitment_by=='department':
            physician = ''

        slot_data = request.env['hms.appointment'].get_slot_data(physician_id, department_id)
        user = request.env['res.users'].sudo().browse(request.uid)
        last_date = fields.Date.today() + timedelta(days=user.company_id.allowed_booking_online_days)

        schedule_slot_id = False
        schedule_slot_name = schedule_slot_date = ''
        if post.get('schedule_slot_id'):
            slot_line = request.env['appointment.schedule.slot.lines'].browse(int(post.get('schedule_slot_id')))
            schedule_slot_name = slot_line.name
            schedule_slot_date = slot_line.slot_id.slot_date
            schedule_slot_id = slot_line.id

        values.update({
            'terms_page_link': user.company_id.acs_appointment_tc,
            'department_id': department_id,
            'department': department,
            'physician_id': physician_id,
            'physician': physician,
            'partner': user.partner_id,
            'slots_data': slot_data,
            'schedule_slot_id': schedule_slot_id,
            'schedule_slot_name': schedule_slot_name,
            'schedule_slot_date': schedule_slot_date,
            'allow_home_appointment': allow_home_appointment,
            'last_date': last_date,
        })
        return values

    @http.route(['/create/appointment'], type='http', auth='public', website=True, sitemap=True)
    def create_appointment(self, redirect=None, **post):
        values = self.create_booking_data()
        values.update({
            'redirect': redirect,
        })
        return request.render("acs_hms_online_appointment.appointment_details", values)

    @http.route(['/get/appointment/data'], type='http', auth='public', website=True, sitemap=False)
    def create_appointment_data(self, redirect=None, **post):
        appoitment_by = post.get('appoitment_by','physician')
        if appoitment_by=='physician' and 'department_id' in post:
            post.pop('department_id')
        if appoitment_by=='department' and 'physician_id' in post:
            post.pop('physician_id')
        values = self.user_booking_data(post)
        return request.render("acs_hms_online_appointment.appointment_slot_details", values)

    @http.route(['/get/appointment/personaldata'], type='http', auth='public', website=True, sitemap=False)
    def appointment_personal_data(self, redirect=None, **post):
        values = self.user_booking_data(post)
        return request.render("acs_hms_online_appointment.appointment_personal_details", values)

    @http.route(['/save/appointment'], type='http', auth='user', website=True, sitemap=False)
    def save_appointment(self, redirect=None, **post):
        env = request.env
        partner = env['res.users'].browse(request.uid).partner_id
        app_obj = env['hms.appointment'].sudo()
        res_patient = env['hms.patient'].sudo()
        slot_line = env['appointment.schedule.slot.lines']
        user = env.user.sudo()
        values = {
            'error': {},
            'error_message': [],
            'partner': partner,
        }

        patient = res_patient.search([('partner_id', '=', partner.id)],limit=1)
        error, error_message = self.validate_application_details(patient, post)
        if error_message:
            values = self.user_booking_data(post)
            values.update({
                'redirect': redirect,
            })
            values.update({'error': error, 'error_message': error_message})
            return request.render("acs_hms_online_appointment.appointment_slot_details", values)

        if post:
            slot = slot_line.browse(int(post.get('schedule_slot_id')))
            now = datetime.datetime.now()
            #user_tz = pytz.timezone(request.context.get('tz') or env.user.tz or 'UTC')
            #app_date = user_tz.localize(slot.from_slot).astimezone(pytz.utc)
            #app_date.replace(tzinfo=None)
            app_date = slot.from_slot
            app_end_date = slot.to_slot

            if app_date < now:
                values.update({'error_message':['Appointment date is past please enter valid.']})
                return request.render("acs_hms_online_appointment.appointment_details", values)

            diff = app_end_date - app_date
            planned_duration = (diff.days * 24) + (diff.seconds/3600)

            post.update({
                'schedule_slot_id': slot.id,
                'booked_online':True,
                'patient_id': patient.id,
                'date': app_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'planned_duration': planned_duration,
                'date_to': app_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'schedule_date': slot.slot_id.slot_date,
            })

            if slot.physician_id:
                post.update({
                    'physician_id': slot.physician_id.id,
                })

            if post.get('location'):
                post.update({
                    'outside_appointment': True,
                })

            post.pop('name', '')
            post.pop('slot_date', '')
            post.pop('physician_name', '')
            post.pop('department_name', '')
            #POP Accept T&C field. if needed can be stored also.
            post.pop('acs_appointment_tc', '')

            # Create Appointment
            app_id = app_obj.sudo().create(post)

            if user.sudo().company_id.allowed_booking_payment:
                app_id.onchange_date_duration()
                app_id.sudo().with_context(acs_online_transaction=True,default_create_stock_moves=False).create_invoice()
                #Instead of validating invoice just set appointment no to make it working on portal payment.
                #app_id.invoice_id.name = app_id.name
                invoice = app_id.invoice_id
                return request.redirect('/my/invoices/%s#portal_pay' %(invoice.id))

            return request.render("acs_hms_online_appointment.appointment_thank_you", {'appointment': app_id})

        return request.redirect('/my/account')

    def validate_application_details(self, patient, data):
        error = dict()
        error_message = []
        mandatory_fields = ['schedule_slot_id']

        #If no patient 
        if not patient:
            error_message.append(_('No patient is linked with user. Please Contact Administration for further support.'))

        if not data.get('schedule_slot_id'):
            error_message.append(_('Please Select Available Appointment Slot Properly.'))

        # Mandatory Field Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message



class PaymentPortal(payment_portal.PaymentPortal):

    @route('/invoice/transaction/<int:invoice_id>', type='json', auth='public')
    def invoice_transaction(self, invoice_id, access_token=None, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int invoice_id: The invoice to pay, as an `account.move` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the invoice id and the access token
        try:
            self._document_check_access('account.move', invoice_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError("The access token is invalid.")

        kwargs['reference_prefix'] = None  # Allow the reference to be computed based on the invoice
        kwargs.pop('custom_create_values', None)  # Don't allow passing arbitrary create values
        tx_sudo = self._create_transaction(
            custom_create_values={'invoice_ids': [Command.set([invoice_id])]}, **kwargs,
        )

        return tx_sudo._get_processing_values()
