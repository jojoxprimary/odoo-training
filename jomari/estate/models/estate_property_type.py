from odoo import fields, models, _, api

class PropertyType(models.Model):
    _name = 'estate.property.type'
    # _inherit = "estate.mixin"
    _description = 'Real Estate Property Type'
    _sql_constraints = [
        ("unique_type_name", "UNIQUE(name)", "Type name should be unique.")
    ]
    _order = "sequence desc"

    sequence = fields.Integer(default=1)
    name = fields.Char(required=True, string="Name")
    
    property_ids = fields.One2many("estate.property", "property_type_id")
    property_count = fields.Integer(compute="_compute_property_count")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for vals in vals:
            self.env["estate.property.tag"].create(
                {
                    "name": vals.get("name")
                }
            )
        return res

    def unlink(self):
        self.property_ids.state = "canceled"
        return super().unlink()

    # for stat button
    @api.depends("property_ids")
    def _compute_property_count(self):
        for rec in self:
            rec.property_count = len(rec.property_ids)

    # for stat button
    def action_open_property_ids(self):
        return {
            "name": _("Related Properties"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "estate.property",
            "target": "current",
            "domain": [("property_type_id", "=", self.id)],
            "context": {
                "default_property_type_id": self.id,
            }
        }