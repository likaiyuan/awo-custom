# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Invoice Line View',
    'version': '0.5',
    'category': 'Account',
    'summary': 'Adds Invoice Line menu item',
    'description': """
Main Features
==================================================
* Add menu item Invoice Lines
* Captures exchange rates as of the invoice dates and shows the base currency\
 amounts in the output. 

    """,
    'author': 'Rooms For (Hong Kong) Limited T/A OSCG',
    'website': 'http://odoo-asia.com',
    'images' : [],
    'depends': ['account', 'sale', 'purchase', 'sale_line_quant'],
    'data': [
         'account_invoice_view.xml',        
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
