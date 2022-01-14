# # -*- coding: utf-8 -*-

from odoo import models, fields, api


# # class custom-api(models.Model):
# #     _name = 'custom-api.custom-api'
# #     _description = 'custom-api.custom-api'

# #     name = fields.Char()
# #     value = fields.Integer()
# #     value2 = fields.Float(compute="_value_pc", store=True)
# #     description = fields.Text()
# #
# #     @api.depends('value')
# #     def _value_pc(self):
# #         for record in self:
# #             record.value2 = float(record.value) / 100

# class InheritedProduct(models.Model):
#     _inherit = "product.product"
    
#     def __init__(self, pool, cr):
#         super().__init__(pool, cr)
    
#     def inherited_action(self):
#         return super().inherited_action()
    
#     @api.model
#     def search(self, args, offset=0, limit=None, order=None, count=False):
#         res = self.env['product.product'].search(args, offset=offset, limit=limit, order=order, count=count)
#         return res

class ProductImage(models.Model):
    _name = "product.custom.image"
    _description = "product.custom.image"
    # _inherit = "product.product"
    
    product_id = fields.Many2one(comodel_name="product.product", ondelete="cascade", string="Product Image")
    url = fields.Char()
