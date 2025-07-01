import random

from odoo import http
from odoo.http import request 
from datetime import datetime, date ,timedelta


class Portalcontroller(http.Controller):

    @http.route('/v1/get/package-details', type='json', auth='public', methods=['GET'])
    def get_package_details(self, *args, **kw):
            try:
                packages = request.env['hop.package.master'].sudo().search([])
                package_list = []
                for values in packages:
                    cat_list = []
                    for line in values.package_line_ids.mapped('category_id'):
                        pack_list= []
                        for res in values.package_line_ids.filtered(lambda l: l.category_id.id == line.id):
                            pack_list.append({
                                'item_name':res.item,
                                'qty':res.qty
                            })
                        cat_list.append({"cat_name":line.name,"data":pack_list})
                    package_list.append({"package":values.name,"data":cat_list})
                return {
                    "packages": package_list,
                    "status_code": 200,
                    "message": "Successful"
                }
            except Exception as e:
                return {'message': _(e.message), 'status_code': 500}
            
    @http.route('/v1/get-package', type='json', auth='public', methods=['GET'])
    def get_package(self, *args, **kw):
            try:
                packages = request.env['hop.package.master'].sudo().search([])
                package_list = []
                for values in packages:
                    package_list.append({'package_name':values.name,'id':values.id})
                return {
                    "packages": package_list,
                    "status_code": 200,
                    "message": "Successful"
                }
            except Exception as e:
                return {'message': _(e.message), 'status_code': 500}
            
    @http.route('/v1/create-inquiry', type='json', auth='public', methods=['POST'])
    def create_inquiry(self, *args, **kw):
            try:
                qcontext = request.params.copy()
                line_list = []
                hours, minutes = map(int, qcontext.get('time',False).split(':'))
                time_in_float = hours + minutes / 60.0
                print(time_in_float) 
                line_list.append((0,0, {
                                    'remarks': qcontext.get('message',False),
                                    'date':datetime.strptime(qcontext.get('date',False), "%Y-%m-%d").date(),
                                    'no_of_pax': qcontext.get('no_of_pax',False),
                                    'time':time_in_float
                                }))
                packages = request.env['hop.calendar'].sudo().create({
                      'name':qcontext.get('name',False),
                      'party_number':str(qcontext.get('number',False)),
                      'email':qcontext.get('email',False),
                      'date':datetime.strptime(qcontext.get('date',False), "%Y-%m-%d").date(),
                      'type':'website',
                      'calendar_line_ids' : line_list,
                      'pkg_list':','.join(qcontext.get('pkg_list',False))
                       })

                return {
                    "status_code": 200,
                    "message": "Successful"
                }
            except Exception as e:
                return {'message': _(e.message), 'status_code': 500}

    
    @http.route('/v1/get/season-recipe', type='json', auth='public', methods=['GET'])
    def get_season_recipe(self, *args, **kw):
        try:
            season_recipe = request.env['hop.season.recipe'].sudo().search([])
            season_list = [
                {
                    'season': line.name,
                    'data': [
                        {
                            'recipe': res.recipe_id.name,
                            'description': res.description,
                            'image': res.image
                        }
                        for res in season_recipe.filtered(lambda l: l.season_id.id == line.id)
                    ]
                }
                for line in season_recipe.mapped('season_id')
            ]
            sorted_season_list = sorted(season_list, key=lambda x: x['season'])

            return {
                "season": sorted_season_list,
                "status_code": 200,
                "message": "Successful"
            }
        except Exception as e:
            return {'message': str(e), 'status_code': 500}
        
    @http.route('/v1/get/customer-detail', type='json', auth='public', methods=['POST'])
    def customer_detail(self, *args, **kw):
            try:
                qcontext = request.params.copy()
                records = request.env['hop.gallery.master'].sudo().search([('type','=',qcontext.get('so',False))])
                list=[]
                for line in records:
                     list.append({
                          'name':line.name,
                          'image':line.logo,
                          'id':line.id
                     })

                return {
                "customer": list,
                "status_code": 200,
                "message": "Successful"
            }
            except Exception as e:
                return {'message': _(e.message), 'status_code': 500}
            
    @http.route('/v1/get/gallery-detail', type='json', auth='public', methods=['POST'])
    def gallery_detail(self, *args, **kw):
            try:
                qcontext = request.params.copy()
                records = request.env['hop.gallery.master'].sudo().search([('id','=',qcontext.get('id',False))])
                image_list=[]
                for line in records.attachment_ids:
                    image_list.append(line.datas)

                menu_list = []
                for line in records.menu_line_ids:
                    menu_list.append(
                         {
                             'category' :line.category_id.name,
                             'item':line.item_id.name,
                             'qty':line.qty
                         }
                    )

                cat_list = []
                for line in records.menu_line_ids.mapped('category_id'):
                    pack_list= []
                    for res in records.menu_line_ids.filtered(lambda l: l.category_id.id == line.id):
                        pack_list.append({
                            'item_name':res.item_id.name,
                            'qty':res.qty
                        })
                    cat_list.append({"cat_name":line.name,"data":pack_list})
                # list =[{"image_data":image_list,'menu_data':cat_list}]
                return {
                "gallery": {"image_data":image_list,'menu_data':cat_list},
                "status_code": 200,
                "message": "Successful"
            }
            except Exception as e:
                return {'message': _(e.message), 'status_code': 500}