from odoo import fields, models

class EstateMixin(models.AbstractModel):
    _name = "estate.mixin"
    _description = "Estate Mixin"
    
    name = fields.Char(required=True)