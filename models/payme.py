# -*- coding: utf-8 -*-

from email.policy import default
from importlib.metadata import requires
from odoo import models, fields, api


class payme(models.Model):
    _name = 'payme.payme'
    _description = 'payme.payme'

    external_id = fields.Char(required=True)
    create_time = fields.Char()
    pay_time = fields.Char()
    cancel_time = fields.Char()
    state = fields.Integer(default=0)
    amount = fields.Integer()
    card = fields.Many2one(comodel_name='payme.card', ondelete='set null', required=False)
    user_id = fields.Many2one(comodel_name='res.users', ondelete="set null")
    order_id = fields.Many2one(comodel_name='sale.order', ondelete="set null")

class card(models.Model):
    _name = 'payme.card'
    _description = 'payme.card'
    
    token = fields.Char(required=True)
    number = fields.Char(required=True)
    expire = fields.Char(required=True)
    verify = fields.Boolean(default=False)
    recurrent = fields.Boolean(default=True)
    owner_id = fields.Many2one(comodel_name='res.users', ondelete="set null")
    deleted = fields.Boolean(default=False)
    
    def __init__(self, pool, cr):
        super().__init__(pool, cr)
        
    
