# -*- coding: utf-8 -*-
{
    'name': "Website Product Personalisation-2.",
    'version': '18.0',
    'category': 'Website',
    'sequence': -1,
    'summary': """
        this module is use for customising the product in the website sale
    """,
    'description': """
        this module is use for customising the product in the website sale
    """,
    'depends': ['website','website_sale','sale_management'],
    'installable': True,
    'application': True,
        'license': 'LGPL-3',
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/product_personalisation.xml',
        'views/product_customisation_view.xml',
        'views/sale_order_line_inherited_view.xml',
    ],
    'assets':{
        "web.assets_frontend": [
            "website_product_personalise_2/static/src/css/fonts.css",
            "website_product_personalise_2/static/src/js/sales_personalise.js",
        ]
    },
}
