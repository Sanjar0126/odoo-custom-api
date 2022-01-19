# -*- coding: utf-8 -*-
from collections import OrderedDict
from odoo import api, http
from . import payme

true=True

class Payme(http.Controller):   
    @http.route('/custom-api/payme/add-card', auth='user', type='json', methods=['POST'], cors="*")
    def add_card(self, **kw):
        params = http.request.params
        
        response = payme.add_card(params)
        
        user_id = http.request.session['uid']

        card_details = response['result']['card']

        response = payme.send_code(card_details['token'])
        
        vals = {
            "token": card_details['token'],
            "number": card_details['number'],
            "expire": card_details['expire'],
            "verify": card_details['verify'],
            "recurrent": card_details['recurrent'],
            "owner_id": user_id,
        }
        
        created_obj = http.request.env['payme.card'].create(vals)
        
        vals["card_id"] = created_obj["id"]
        
        return vals
        
    @http.route('/custom-api/payme/verify', auth='user', type='json', methods=['POST'], cors="*")
    def verify_card(self, **kw):
        params = http.request.params
        
        card = http.request.env['payme.card'].search([("id",'=',params['card_id'])], limit=1)
        
        if len(card)==0:
            return {"error": "no card found"}
        
        response = payme.verify_code(params['code'], card[0]['token'])
        
        card.write({"verify": True, "recurrent": response['result']['card']['recurrent']})
        
        return {
            "success": True
        }
        
    @http.route('/custom-api/payme/card-list', auth='user', type='json', methods=['POST'], cors="*")
    def card_list(self, **kw):
        params = http.request.params
        user_id = http.request.session['uid']
        
        cards = http.request.env['payme.card'].search([("owner_id",'=',user_id), ("deleted", "=", False)])
        
        result = []
        
        for card in cards:
            result.append(OrderedDict({
                "id": card["id"],
                "number": card["number"],
                "expire": card["expire"],
                "create_date": card["create_date"],
                "verify": card["verify"],
                "recurrent": card["recurrent"],
                "owner_id": card["owner_id"][0]["id"],
            }))
        
        return result
    
    @http.route('/custom-api/payme/card-remove', auth='user', type='json', methods=['POST'], cors="*")
    def card_remove(self, **kw):
        params = http.request.params
        user_id = http.request.session['uid']
        
        card = http.request.env['payme.card'].search([("id",'=',params['card_id'])], limit=1)
        
        if len(card)==0:
            return {"error": "no card found"}
                
        card.write({"deleted": True})
        
        return {"success": True}

    @http.route('/custom-api/payme/receipt', auth='user', type='json', methods=['POST'], cors="*")
    def create_receipt(self, **kw):
        params = http.request.params
        user_id = http.request.env.context.get('uid')
        
        if params['order_id'] is None:
            return {'error': 'no order_id'}
        
        response = payme.create_receipt(params['amount'])
        
        vals = {
            'external_id': response['result']['receipt']['_id'],
            'create_time': str(response['result']['receipt']['create_time']),
            'pay_time': str(response['result']['receipt']['pay_time']),
            'cancel_time': str(response['result']['receipt']['cancel_time']),
            'state': response['result']['receipt']['state'],
            'amount': response['result']['receipt']['amount'],
            'user_id': user_id,
            'order_id': params['order_id'],
        }
        
        receipt = http.request.env['payme.payme'].create([vals])
        
        vals['id'] = receipt[0]['id']
        
        return vals

    @http.route('/custom-api/payme/receipt-pay', auth='user', type='json', methods=['POST'], cors="*")
    def pay_receipt(self, **kw):
        params = http.request.params
        
        user_id = http.request.env.context.get('uid')
        
        payme_receipt = http.request.env['payme.payme'].search([('id', '=', params['receipt_id'])], limit=1)[0]
        
        payme_card = http.request.env['payme.card'].search([('id', '=', params['card_id'])], limit=1)[0]
        
        payme_response = payme.pay_receipt(payme_receipt['external_id'], payme_card['token'])
        
        sale_order = http.request.env['sale.order'].search([('id', '=', payme_receipt['order_id'][0]['id'])], limit=1)[0]
        sale_order.write({'state': 'sale'})
        
        return {"succes": True}
