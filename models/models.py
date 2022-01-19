# # -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductImage(models.Model):
    _name = "product.custom.image"
    _description = "product.custom.image"
    # _inherit = "product.product"
    
    product_id = fields.Many2one(comodel_name="product.product", ondelete="cascade", string="Product Image")
    url = fields.Char()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payme_url = fields.Char(string='payme',
                             config_parameter="payme.payme")
    payme_key = fields.Char(string='payme',
                             config_parameter="payme.payme")
    payme_id = fields.Char(string='payme',
                             config_parameter="payme.payme")

