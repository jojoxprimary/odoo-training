from odoo import fields, models, api, _
from odoo.exceptions import UserError

class RealEstate(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property Model'
    _sql_constraints = [
        ("positive_expected_price", "CHECK(expected_price > 0)", "Property expected price must be positive."),
        # no need for selling price since offer price already has a constraint
    ]
    _order = "id desc"

    active = fields.Boolean(default=True) 
    name = fields.Char(required=True, string="Name")
    postcode = fields.Char(string="Postcode", index=True)
    state = fields.Selection([
        ('new', 'New'),
        ('received', 'Offer Received'),
        ('accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ],
    required=True,
    copy=False,
    default='new',
    compute="_check_state",
    store="True",
    )

    def _default_availability(self):
        return fields.Date.today()

    date_availability = fields.Date(default=_default_availability, copy=False)
    expected_price = fields.Float(string="Expected Price")
   
    selling_price = fields.Float(readonly=True, copy=False)
    buyer = fields.Char(readonly=True, copy=False)

    description = fields.Text()
    bedrooms = fields.Integer(default=2, string="Bedrooms")
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
   
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ])

    property_type_id = fields.Many2one('estate.property.type', string="Property Type")

    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (sqm)")
    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = (property.garden_area) + (property.living_area)

    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")

    best_offer = fields.Float( compute='_compute_best_price', string="Best Offer")
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for property in self:
            if property.offer_ids:
                property.best_offer = max(property.offer_ids.mapped('price'))
            else:
                property.best_offer = 0.0

    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    partner_id = fields.Char(related="offer_ids.partner_id.name", string="Partner")
    
    @api.onchange("garden")
    def _onchange_garden(self):
        for rec in self:
            if not rec.garden:
                rec.garden_area = 0
        
    @api.onchange("date_availability")
    def _onchange_date_availability(self):
        for rec in self:
            if rec.date_availability < fields.Date.today():
                return{
                    "warning": {
                        "title": _("Warning"),
                        "message": _("You are setting the availability date to the past."),
                    }
                }
    
    @api.depends('offer_ids.status')
    def _check_state(self):
        for rec in self:
            if rec.state in ['sold', 'canceled']:
                continue
            if not rec.offer_ids:
                rec.state = 'new'
            elif any(offer.status == 'accepted' for offer in rec.offer_ids):
                rec.state = 'accepted'
            elif rec.offer_ids:
                rec.state = 'received'
            
    def button_property_sold(self):
        for rec in self:
            if not rec.state == 'accepted':
                raise UserError(_("You cannot set the property as sold if no offer is accepted."))
            elif rec.state == "canceled":
                raise UserError(_("Canceled properties cannot be set as sold."))
            rec.state = "sold"
            return True
    
    def button_property_cancel(self):
        for rec in self:
            if rec.state == "sold":
                raise UserError(_("You cannot cancel a sold property"))
            rec.state = "canceled"
            return True

    # Selling price percentage constraint will be validated in the offer model
   
    @api.ondelete(at_uninstall=False)
    def _prevent_delete_not_new_canceled(self):
        for rec in self:
            if rec.state not in ('new', 'canceled'):
                raise UserError(_(
                    "You cannot delete a property that is not new or canceled."
                ))