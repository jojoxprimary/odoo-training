from odoo import fields, models, _

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    # _inherit = "estate.mixin"
    _description = 'Tags of Real Estate Model'
    _sql_constraints = [
        ("unique_tag_name", "UNIQUE(name)", "Tag name should be unique.")
    ]
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()
