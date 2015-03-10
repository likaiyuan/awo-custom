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

from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
        
    def _get_vals(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        SO = self.pool.get('sale.order')
        PO = self.pool.get('purchase.order')
        for invoice_line in self.browse(cr, uid, ids, context=context):
            so_id = 0
            po_id = 0
            if invoice_line.invoice_id.reference:
                if invoice_line.invoice_id.type == 'out_invoice':
                    so_id = SO.search(cr, uid, [('name','=',invoice_line.invoice_id.reference)])[0]
                if invoice_line.invoice_id.type == 'in_invoice':
                    po_id = PO.search(cr, uid, [('name','=',invoice_line.invoice_id.reference)])[0]
            res[invoice_line.id] = {
                'so_id': so_id,
                'po_id': po_id,
                }
        return res
    
    def _get_base_amt(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        Invoice = self.pool.get('account.invoice')
        for invoice_line in self.browse(cr, uid, ids, context=context):
            curr_amt = invoice_line.price_subtotal
            # set the rate 1.0 if the transaction currency is the same as the base currency
            if invoice_line.company_id.currency_id == invoice_line.currency_id:
                rate = 1.0
            else:
                invoice_date = Invoice.browse(cr, uid, [invoice_line.invoice_id.id])[0].date_invoice
                if invoice_date:
                    invoice_date_datetime = datetime.strptime(invoice_date, '%Y-%m-%d')
                else:
                    today = context.get('date', datetime.today().strftime('%Y-%m-%d'))
                    invoice_date_datetime = datetime.strptime(today, '%Y-%m-%d')

                rate_obj = self.pool['res.currency.rate']
                rate_id = rate_obj.search(cr, uid, [
                    ('currency_id', '=', invoice_line.currency_id.id),
                    ('name', '<=', invoice_date_datetime),
                    # not sure for what purpose 'currency_rate_type_id' field exists in the table, but keep this line just in case
                    ('currency_rate_type_id', '=', None)
                    ], order='name desc', limit=1, context=context)
                if rate_id:
                    rate = rate_obj.browse(cr, uid, rate_id, context=context)[0].rate
                else:
                    rate = 1.0
            res[invoice_line.id] = {
                'rate': rate,
                'base_amt': curr_amt / rate,
                }
        return res

    """ return all the invoice lines for the updated invoice """
    def _get_invoice_lines(self, cr, uid, ids, context=None):
        inv_ln_ids = []
#         for invoice in self.browse(cr, uid, ids, context=context):
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
            inv_ln_ids += \
                self.pool.get('account.invoice.line').search(cr, uid,
#                 [('invoice_id.id', '=', invoice.id)], context=context)
                [('invoice_id.id', 'in', ids)], context=context)
        return inv_ln_ids


    _order = 'id desc'
    """ some fields are defined with 'store' for grouping purpose """
    _columns ={
        'user_id': fields.related('invoice_id','user_id',type='many2one',relation='res.users',string=u'Salesperson'),
        'number': fields.related('invoice_id','number',type='char',relation='account.move',string=u'Number'),
        'state': fields.related('invoice_id', 'state', type='char', relation='account.invoice', string=u'Status',
            store={
                   # update is done when 'state' of 'account.invoice' is updated
                   'account.invoice': (_get_invoice_lines, ['state'], 10),
                   },
            multi='invoice',
            ),
        'date_invoice': fields.related('invoice_id', 'date_invoice', type='date', string=u'Invoice Date',
            store={
                   # include 'state' to make sure update is triggered at invoice validation
                   'account.invoice': (_get_invoice_lines, ['date_invoice','state'], 10), 
                   },
            multi='invoice',
            ),
        'period_id': fields.related('invoice_id', 'period_id', type='many2one', relation='account.period', string=u'Period'),
        'reference': fields.related('invoice_id','reference',type='char',string=u'Invoice Ref'),
        'date_due': fields.related('invoice_id','date_due',type='date',string=u'Due Date'),
        'currency_id': fields.related('invoice_id','currency_id',relation='res.currency', type='many2one',string=u'Currency'),
        'rate': fields.function(_get_base_amt, type='float', string=u'Rate', multi='base_amt'),
        'base_amt': fields.function(_get_base_amt, type='float', digits_compute=dp.get_precision('Account'), string=u'Base Amount', multi="base_amt"),
        'partner_id': fields.related('invoice_id', 'partner_id', type='many2one', relation='res.partner', string=u'Partner',
            store={
                   # include 'state' to make sure update is triggered at invoice validation
                   'account.invoice': (_get_invoice_lines, ['partner_id','state'], 10),
                   },
            multi='invoice',
            ),
        'ref': fields.related('invoice_id', 'partner_id', 'ref', type='char', relation='res.partner', string=u'Partner Ref',
            store={
                   # include 'state' to make sure update is triggered at invoice validation
                   'account.invoice': (_get_invoice_lines, ['partner_id','state'], 10),
                   },
            multi='invoice',
            ),
        'so_id': fields.function(_get_vals, type='many2one',
            obj='sale.order', string='SO',
            store={
                   # include 'state' to make sure update is triggered at invoice validation
#                    'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                   'account.invoice': (_get_invoice_lines, ['partner_id','state'], 10),
                   },
            multi="reference"
            ),
        'po_id': fields.function(_get_vals, type='many2one',
            obj='purchase.order', string='PO',
            store={
                   # include 'state' to make sure update is triggered at invoice validation
#                    'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                   'account.invoice': (_get_invoice_lines, ['partner_id','state'], 10),
                   },
            multi="reference"
            ),
        }

    def init(self, cr):
        # to be executed only when installing the module.  update "stored" fields 
        cr.execute("update account_invoice_line line \
                    set state = inv.state, date_invoice = inv.date_invoice, partner_id = inv.partner_id \
                    from account_invoice inv \
                    where line.invoice_id = inv.id")

account_invoice_line()