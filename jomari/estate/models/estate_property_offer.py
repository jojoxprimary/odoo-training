from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta 

class EstateOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Offers made for real estates'
    _sql_constraints = [
        ("positive_offer_price", "CHECK(price > 0)","Offer price must be positive.")
    ]

    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False,
    )
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    property_type = fields.Char(related="property_id.property_type_id.name", string="Property Type", store=True)

    date_deadline = fields.Date(string="Deadline", compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    
    create_date = fields.Datetime("Creation Date", readonly=True, default=fields.Datetime.now)

    validity = fields.Integer(string="Validity", default=7)

    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.date_deadline = offer.create_date.date() + timedelta(days=offer.validity)
            else:
                offer.date_deadline = False 

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.date_deadline and offer.create_date:
                offer.validity = (offer.date_deadline - offer.create_date.date()).days   
            
    def action_accept(self):
        self.ensure_one()
        if "accepted" in self.property_id.offer_ids.mapped('status'):
            raise UserError(_("An offer has already been accepted."))
        self.status = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer = self.partner_id.name

    def action_refuse(self):
        self.ensure_one()
        self.status = "refused"

    @api.constrains('price', 'property_id.expected_price')
    def _check_offer_price(self):
        for offer in self:
            if offer.property_id and offer.price < (offer.property_id.expected_price * 0.9):
                raise ValidationError(_(
                    "Offer price cannot be lower than 90%% of the expected price (Minimum: %s)"
                ) % (offer.property_id.expected_price * 0.9))
    
    @api.constrains('price', 'property_id')
    def _check_offer_amount(self):
        for offer in self:
            if offer.property_id.offer_ids:
                max_offer = max(offer.property_id.offer_ids.mapped('price'))
                if offer.price <= max_offer:
                    raise ValidationError(_(
                        "Offer price must be higher than %(amount)s",
                        amount=max_offer
                    ))
