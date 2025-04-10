{
    "name": "Real Estate",
    "summary": "Test",
    "license": "OEEL-1",
    "version": "18.0.0.0.0",
    "depends": ["crm"],
    "data": [
       
        # SECURITY
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        # VIEWS
        "views/estate_property_view.xml",
        "views/estate_property_type_view.xml",
        "views/estate_property_offer_view.xml",
        "views/estate_property_tag_view.xml",
         # MENUS
        "views/estate_menus.xml",
    ],
}