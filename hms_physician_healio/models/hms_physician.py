# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
import requests
import urllib.parse
from odoo.exceptions import UserError

class Physician(models.Model):
    _inherit = 'hms.physician'
    latitude = fields.Float(string='Geo Latitude', digits=(4, 9))
    longitude = fields.Float(string='Geo Longitude', digits=(4, 9))
    
    '''@api.onchange('street', 'street2', 'city', 'zip', 'country_id')
    def get_coordinate(self):
        for rec in self:
            street = rec.street or ''
            street2 = rec.street2 or ''
            city = rec.city or ''
            zip_code = rec.zip or ''
            country = rec.country_id.name or ''

            if street or city or zip_code or country:
                address_components = [street, city, zip_code, country]
                address = '%2C+'.join(filter(None, address_components)).strip()
                # Replace spaces with '+'
                encoded_address = address.replace(' ', '+')
                url = 'https://nominatim.openstreetmap.org/search?q=' + encoded_address + '?format=json'
                #address = (street + ', ' + city + ', ' + zip_code + ', ' + country).strip()
                #url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'

                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for non-2xx responses
                    data = response.json()

                    if data:
                        rec.latitude = float(data[0]["lat"])
                        print("HEREEEEE LAT!!!!!!!!!!!!!!!!!!!!!!!! ")
                        print(rec.latitude)
                        rec.longitude = float(data[0]["lon"])
                        print("HEREEEEE LONG!!!!!!!!!!!!!!!!!!!!!!!! ")
                        print(rec.longitude)
                    else:
                        rec.latitude = False
                        rec.longitude = False
                except requests.exceptions.RequestException as e:
                    # Handle connection or request-related errors
                    rec.latitude = False
                    rec.longitude = False
                    print("Error:", e)
                except (KeyError, IndexError):
                    # Handle JSON decoding errors or missing data
                    rec.latitude = False
                    rec.longitude = False
                    print("JSON decoding error or missing data")'''
                    
    @api.onchange('street', 'street2', 'city', 'zip', 'country_id')
    def get_coordinate(self):
        for rec in self:
            street = rec.street or ''
            street2 = rec.street2 or ''
            city = rec.city or ''
            zip_code = rec.zip or ''
            country = rec.country_id.name or ''

            if street or city or zip_code or country:
                # Construct the address based on available fields
                address_components = [street, street2, city, zip_code, country]
                address = ', '.join(filter(None, address_components)).strip()

                # Get coordinates using the get_coordinates function
                lat, lon = self.get_coordinates(address)

                # Update latitude and longitude fields on the record
                rec.latitude = lat
                rec.longitude = lon

    def get_coordinates(self, address):
        base_url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json'
        }
        url = base_url + '?' + urllib.parse.urlencode(params)

        headers = {
            'User-Agent': 'Odoo backend'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(lat)
                print(lon)
                return lat, lon
            else:
                print('No location data found for the address:', address)
                return False, False

        except requests.exceptions.RequestException as e:
            print('Error connecting to the API:', e)
            return False, False
        except (KeyError, IndexError) as e:
            print('Error parsing API response:', e)
            return False, False                
                    
    '''@api.model
    def get_physician_list(self):
        physicians = self.search([])
        physician_list = []
        for physician in physicians:
            physician_dict = {
                'doc_id': physician.id,
                'name': physician.name,
                'speciality': physician.specialty_id.name,
                'address': physician.state_id and physician.state_id.name or False,
                'phone': physician.phone,
                'email': physician.email,
            }
            physician_list.append(physician_dict)
        return {'res_code': '1', 'physician_list': physician_list}'''
    
    '''@api.model
    def search_physicians_by_name(self, name):
        physicians = self.search([('name', 'ilike', name)])
        physician_list = []
        for physician in physicians:
            physician_dict = {
                'doc_id': physician.id,
                'name': physician.name,
                'speciality': physician.specialty_id.name,
                'address': physician.state_id and physician.state_id.name or False,
                'phone': physician.phone,
                'email': physician.email,
            }
            physician_list.append(physician_dict)
        return {'res_code': '1', 'physician_list': physician_list}'''
    
    '''@api.model
    def filter_physicians(self, region=None, specialty=None):
        domain = []
        if region:
            domain += [('state_id.name', 'ilike', region)]
        if specialty:
            domain += [('specialty_id.name', 'ilike', specialty)]
        
        physicians = self.search(domain)
        physician_list = []
        for physician in physicians:
            physician_dict = {
                'doc_id': physician.id,
                'name': physician.name,
                'speciality': physician.specialty_id.name,
                'address': physician.state_id and physician.state_id.name or False,
                'phone': physician.phone,
                'email': physician.email,
            }
            physician_list.append(physician_dict)
        return {'res_code': '1', 'physician_list': physician_list}'''



    
    
    @api.model
    def get_physician_list(self, vals):
        try:
            page = vals.get('page', 1)
            page_size = vals.get('page_size', 10)
            physicians = self.search([], limit=page_size, offset=(page - 1) * page_size)
            physician_list = []
            for physician in physicians:
                physician_dict = {
                    'doc_id': physician.id,
                    'name': physician.name,
                    'speciality': physician.specialty_id.name,
                    'address': physician.state_id.name if physician.state_id else False,
                    'phone': physician.phone,
                    'email': physician.email,
                }
                physician_list.append(physician_dict)

            # Count total number of records
            total_count = self.search_count([])

            # Calculate total pages based on total count and page size
            total_pages = (total_count + page_size - 1) // page_size  # Using ceiling division

            return {'res_code': '1', 'physician_list': physician_list, 'total_pages': total_pages, 'total_count': total_count}
        except Exception as e:
            print('Error in get_physician_list:', e)
            return {'res_code': '5', 'physician_list': [], 'total_pages': 0, 'total_count': 0}

        
    @api.model
    def search_physicians_by_name(self, vals):
        try:
            page = vals.get('page', 1)
            page_size = vals.get('page_size', 10)
            name = vals.get('name', '')
            physicians = self.search([('name', 'ilike', name)], limit=page_size, offset=(page - 1) * page_size)
            physician_list = []
            for physician in physicians:
                physician_dict = {
                    'doc_id': physician.id,
                    'name': physician.name,
                    'speciality': physician.specialty_id.name,
                    'address': physician.state_id.name if physician.state_id else False,
                    'phone': physician.phone,
                    'email': physician.email,
                }
                physician_list.append(physician_dict)

            # Count total number of records that match the search criteria
            total_count = self.search_count([('name', 'ilike', name)])

            # Calculate total pages based on total count and page size
            total_pages = (total_count + page_size - 1) // page_size  # Using ceiling division

            return {'res_code': '1', 'physician_list': physician_list, 'total_pages': total_pages, 'total_count': total_count}
        except Exception as e:
            print('Error in get_physician_list:', e)
            return {'res_code': '5', 'physician_list': [], 'total_pages': 0, 'total_count': 0}

        
    @api.model
    def filter_physicians(self, vals):
        try:
            page = vals.get('page', 1)
            page_size = vals.get('page_size', 10)
            region = vals.get('region', '')
            specialty = vals.get('specialty', '')
            domain = []
            if region:
                domain += [('state_id.name', 'ilike', region)]
            if specialty:
                domain += [('specialty_id.name', 'ilike', specialty)]
            physicians = self.search(domain, limit=page_size, offset=(page - 1) * page_size)
            physician_list = []
            for physician in physicians:
                physician_dict = {
                    'doc_id': physician.id,
                    'name': physician.name,
                    'speciality': physician.specialty_id.name,
                    'address': physician.state_id.name if physician.state_id else False,
                    'phone': physician.phone,
                    'email': physician.email,
                }
                physician_list.append(physician_dict)

            # Count total number of records that match the search criteria
            total_count = self.search_count(domain)

            # Calculate total pages based on total count and page size
            total_pages = (total_count + page_size - 1) // page_size  # Using ceiling division

            return {'res_code': '1', 'physician_list': physician_list, 'total_pages': total_pages, 'total_count': total_count}
        except Exception as e:
            print('Error in get_physician_list:', e)
            return {'res_code': '5', 'physician_list': [], 'total_pages': 0, 'total_count': 0}


    @api.model
    def get_physician_details(self, vals):
        try:
            physician_id = vals.get('id', False)
            if not physician_id:
                return {'res_code': '-1', 'error': 'Physician ID not provided'}
            physician = self.browse(physician_id)
            if not physician:
                return {'res_code': '-1', 'error': 'Physician not found'}

            physician_details = {
                'doc_id': physician.id,
                'name': physician.name,
                'speciality': physician.specialty_id.name,
                'address': physician.state_id and physician.state_id.name or False,
                'phone': physician.phone,
                'email': physician.email,
            }
            return {'res_code': '1', 'physician_details': physician_details}
        except Exception as e:
            print('Error in get_physician_details:', e)
            return {'res_code': '5', 'physician_details': None}





