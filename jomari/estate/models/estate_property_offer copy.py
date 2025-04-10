from odoo import fields, models

class PropertyOffer(models.Model):
    _name = "new_estate.property.offer"
    _inherit="estate.property.offer"

    account_move_id = fields.Many2one("account.move", string="Invoice", readonly=True)