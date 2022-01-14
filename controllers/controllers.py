# -*- coding: utf-8 -*-
from odoo import http
import json
from odoo.tools import date_utils
import collections


MINIO_URL = "http://192.168.1.107:9000/images"

class CustomApi(http.Controller):
    @http.route('/custom-api/product.product', auth='public', type='http', methods=['GET'])
    def get_products(self, **kw):
        limit = int(kw.get('limit', 10))
        page = int(kw.get('page', 1))
        name = kw.get('name', None)
        
        filter = []
        if name:
            filter.append(("name", "ilike", name))
                        
        products = http.request.env['product.product'].search(filter, limit=limit, offset=(page-1)*limit)
        count = http.request.env['product.product'].search_count([])
        result = []
        for item in products:
            thumbs = []
            images = http.request.env['product.custom.image'].search([('product_id', '=', item.id)])
            for img in images:
                thumbs.append(f"{MINIO_URL}{img.url}")
            
            result.append({
                "id":           item.id,
                "name":         item.name,
                "list_price":   item.list_price,
                "active":       item.active,
                "purchase_ok":  item.purchase_ok,
                "default_code": item.default_code,
                "description_sale": item.description_sale,
                "detailed_type": item.detailed_type,
                "type": item.type,
                "category": {
                    "id": item.categ_id.id,
                    "name": item.categ_id.name,
                    "complete_name": item.categ_id.complete_name,
                },
                "sale_ok": item.sale_ok,
                "purchase_ok": item.purchase_ok,
                "is_published": item.is_published,
                "images": thumbs
            })
        return http.Response(json.dumps(
            {
            "products": result, 
            "count": count,
            "page": page
            },
        ensure_ascii=False).encode('utf8'), headers = {'Content-Type': 'application/json'})
    
    @http.route('/custom-api/product.product/<model("product.product"):item>', auth='public', type='http', methods=['GET'])
    def get_single_product(self, item, **kw):
        thumbs = []
        images = http.request.env['product.custom.image'].search([('product_id', '=', item.id)])
        for img in images:
            thumbs.append(f"{MINIO_URL}{img.url}")
        result = {
            "id":           item.id,
            "name":         item.name,
            "list_price":   item.list_price,
            "active":       item.active,
            "purchase_ok":  item.purchase_ok,
            "default_code": item.default_code,
            "description_sale": item.description_sale,
            "detailed_type": item.detailed_type,
            "type": item.type,
            "category": {
                "id": item.categ_id.id,
                "name": item.categ_id.name,
                "complete_name": item.categ_id.complete_name,
            },
            "sale_ok": item.sale_ok,
            "purchase_ok": item.purchase_ok,
            "is_published": item.is_published,
            "website_description": item.website_description,
            "images": thumbs
        }
        return http.Response(json.dumps(result, ensure_ascii=False).encode('utf8'), headers = {'Content-Type': 'application/json'})

    @http.route(route="/custom-api/order", type='json', methods=["POST"], auth="user", csrf=False)
    def create_order(self, **kw):
        params = http.request.params

        user_id = http.request.session['uid']
        session_id = http.request.session['session_token']
        
        sale_count = http.request.env['sale.order'].search_count([])
        
        products = []
        untaxed = taxed = total = 0
        
        for item in params['products']:
            product = http.request.env['product.product'].search([('id', '=', item['id'])], limit=1)[0]
            
            tax_amount = product['taxes_id'][-1]['amount']
            
            products.append({
                "name": product['partner_ref'],
                "product_id": product['id'],
                'invoice_status': 'no',
                'product_uom_qty': item['quantity'],
                'qty_delivered_method': 'stock_move', #idk what is this
                'currency_id': 1, 
                'order_partner_id': user_id,
            })
            
        values = [{
            "name": f"S{sale_count+1}",
            "reference": f"S{sale_count+1}",
            "access_token": session_id,
            "state": params['state'],
            "user_id": user_id,
            "partner_id": user_id,
            "partner_invoice_id": user_id,
            "partner_shipping_id": user_id,
            "currency_id": 1,
            "note": params['note'],
            "website_id": 1,
        }]
        new_order = http.request.env['sale.order'].create(values)
        
        for item in products:
            item.update({'order_id': new_order[0]['id']})
        
        order_line = http.request.env['sale.order.line'].create(products)
        return {"success": True}
    
    @http.route(route='/custom-api/order/<model("sale.order"):order_item>', type='json', methods=["PATCH"], auth="user", csrf=False)
    def order_update(self, order_item, *args, **kwargs):    
        params = http.request.params
        
        sale_order = http.request.env['sale.order'].search([('id', '=', order_item['id'])], limit=1)
        
        sale_order[0].write({
            "state": params['state']
        })
        
        return {"success": True}
    
    @http.route(route='/custom-api/order/<model("sale.order"):order_item>', type='json', methods=["GET"], auth="user", csrf=False)
    def get_order(self, order_item, *args, **kwargs):
        order_line = []
        for item in order_item['order_line']:
            order_line.append({
                "id": item["id"],
                "name": item["name"],
                "price_unit": item["price_unit"],
                "price_subtotal": item["price_subtotal"],
                "price_tax": item["price_tax"],
                "price_total": item["price_total"],
                "quantity": item["product_uom_qty"],
                "qty_delivered_method": item["qty_delivered_method"],
                "qty_delivered": item["qty_delivered"],
                "state": item["state"],
                "create_date": item["create_date"],
            })
            
        result = {
            "id": order_item["id"],
            "name": order_item['name'],
            'state': order_item['state'],
            'date_order': order_item['date_order'],
            'require_signature': order_item['require_signature'],
            'require_payment': order_item['require_payment'],
            "user": None if order_item['user_id'] is None else {
                "id": order_item['user_id']['id'],
                "login": order_item['user_id']['login'],
                "active": order_item['user_id']['active']
            },
            "customer": None if order_item['partner_id'] is None else {
                "id": order_item['partner_id']['id'],
                "name": order_item['partner_id']['name'],
                "display_name": order_item['partner_id']['display_name'],
                "website": order_item['partner_id']['website'],
                "active": order_item['partner_id']['active'],
                "function": order_item['partner_id']['function'],
                "street": order_item['partner_id']['street'],
                "zip": order_item['partner_id']['zip'],
                "city": order_item['partner_id']['city'],
                "email": order_item['partner_id']['email'],
                "phone": order_item['partner_id']['phone'],
                "is_company": order_item['partner_id']['is_company'],
                "commercial_company_name": order_item['partner_id']['commercial_company_name'],
            },
            "currency": None if order_item['currency_id'] is None else {
                "id": order_item['currency_id']['id'],
                "name": order_item['currency_id']['name'],
                "full_name": order_item['currency_id']['full_name'],
                "currency_unit_label": order_item['currency_id']['currency_unit_label'],
                "symbol": order_item['currency_id']['symbol'],
            },
            "note": order_item['note'],
            "amount_untaxed": order_item['amount_untaxed'],
            "amount_tax": order_item['amount_tax'],
            "amount_total": order_item['amount_total'],
            "currency_rate": order_item['currency_rate'],
            "picking_policy": order_item['picking_policy'],
            "order_line": order_line,
        }
        return result
    
    @http.route(route="/custom-api/order", type='json', methods=["GET"], auth="user", csrf=False)
    def get_order_list(self, *args, **kwargs):
        limit = int(kwargs.get('limit', 10))
        page = int(kwargs.get('page', 1))
        name = kwargs.get('name', None)
        user_id = http.request.session['uid']
        
        filter = [("partner_id", "=", user_id)]
        if name:
            filter.append(("name", "ilike", name))
            
        orders = http.request.env['sale.order'].search(filter, limit=limit, offset=(page-1)*limit)
        count = http.request.env['sale.order'].search_count(filter)

        result = list()
        
        for order_item in orders:
            order_line = []
            for item in order_item['order_line']:
                order_line.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price_unit": item["price_unit"],
                    "price_subtotal": item["price_subtotal"],
                    "price_tax": item["price_tax"],
                    "price_total": item["price_total"],
                    "quantity": item["product_uom_qty"],
                    "qty_delivered_method": item["qty_delivered_method"],
                    "qty_delivered": item["qty_delivered"],
                    "state": item["state"],
                    "create_date": item["create_date"],
                })
            result.append({
                "id": order_item["id"],
                "name": order_item['name'],
                'state': order_item['state'],
                'date_order': order_item['date_order'],
                'require_signature': order_item['require_signature'],
                'require_payment': order_item['require_payment'],
                "user": None if order_item['user_id'] is None else {
                    "id": order_item['user_id']['id'],
                    "login": order_item['user_id']['login'],
                    "active": order_item['user_id']['active']
                },
                "customer": None if order_item['partner_id'] is None else {
                    "id": order_item['partner_id']['id'],
                    "name": order_item['partner_id']['name'],
                    "display_name": order_item['partner_id']['display_name'],
                    "website": order_item['partner_id']['website'],
                    "active": order_item['partner_id']['active'],
                    "function": order_item['partner_id']['function'],
                    "street": order_item['partner_id']['street'],
                    "zip": order_item['partner_id']['zip'],
                    "city": order_item['partner_id']['city'],
                    "email": order_item['partner_id']['email'],
                    "phone": order_item['partner_id']['phone'],
                    "is_company": order_item['partner_id']['is_company'],
                    "commercial_company_name": order_item['partner_id']['commercial_company_name'],
                },
                "currency": None if order_item['currency_id'] is None else {
                    "id": order_item['currency_id']['id'],
                    "name": order_item['currency_id']['name'],
                    "full_name": order_item['currency_id']['full_name'],
                    "currency_unit_label": order_item['currency_id']['currency_unit_label'],
                    "symbol": order_item['currency_id']['symbol'],
                },
                "note": order_item['note'],
                "amount_untaxed": order_item['amount_untaxed'],
                "amount_tax": order_item['amount_tax'],
                "amount_total": order_item['amount_total'],
                "currency_rate": order_item['currency_rate'],
                "picking_policy": order_item['picking_policy'],
                "order_line": order_line
            })
        return collections.OrderedDict({
            "orders": result, 
            "count": count,
            "page": page
            })
