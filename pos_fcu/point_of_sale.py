# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017- Vertel (<http://vertel.se>).
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
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning

from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    """ POS order  """
    _inherit = 'pos.config'

    iface_fcu = fields.Boolean(string="Financial Control Unit")
    fcu_contract = fields.Char(string="FCU Contract")
    fcu_server = fields.Char("FCU Server (http://server[:port])")

class pos_order(models.Model):
    """ POS order  """
    _inherit = 'pos.order'

    fcu_id = fields.Char()

    #~ @api.multi
    #~ def action_done(self):
        #~ _logger.error('POS: %s' % self)
        #~ for s in self:
            #~ _logger.error('POS: %s' % s)
            #~ super(pos_order, s).action_done()
            #~ raise Warning('Action Done')
        #~ return True

    #~ @api.multi
    #~ def create_from_ui(self,orders):
        #~ _logger.error('POS: %s' % orders)
        #~ for s in self:
            #~ o_list = super(pos_order, s).create_from_ui(orders)
        #~ return o_list
        #~ #raise Warning('Action create_from_ui %s %s %s' % (orders,o_list,self))



    def _process_order(self,cr, uid, order, context=None):
        _logger.error('POS: %s' % order)
        order_id = super(pos_order, self)._process_order(cr,uid,order,context)
        _logger.error('POS: %s' % order_id)
        o = self.browse(cr,uid,order_id)
        # pos_client = fcu_post({'reciept':''},contract,app_id)
        o.fcu_id = "controle_code"  # get controle_code


#pos_fcu.py

import jsonrpclib

class fcu_post(object):

    def __init__(self):
        # server proxy object
        url = "http://%s:%s/jsonrpc" % ('localhost', '8069')
        server = jsonrpclib.Server(url)

        # log in the given database
        uid = server.call(service="common", method="login", args=['pos', 'admin', 'admin'])

        # helper function for invoking model methods
        def invoke(model, method, *args):
            args = ['pos', uid, 'admin', model, method] + list(args)
            return server.call(service="object", method="execute", args=args)

        # create a new note
        args = {
            'name' : 'anders',
            'login' : 'This is another note',
            'create_uid': uid,
        }
        note_id = invoke('res.users', 'search', [('name','ilike','Demo User')])
        for u in note_id:
            print u
            print u['name']
        #~ note_id = invoke('note.note', 'create', args)



class pos_fcu_json(http.Controller):

    @http.route(['/pos_fcu/<string:form_name>/add', ], type='json', auth="none",)
    def fcu_add(self, form_name=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        return {
            'form_name': form_name,
            #'appcert': appcert,
            'uid': uid,
            'context': context,
#            'request.method': request.method,
#            'request.args': request.args,
            'post': post,
        }
    @http.route(['/post_fcu/<string:contract>/post', ], type='json', auth="public",)
    def fcu_post(self,contract=None,appcert=None,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        contract = request.env['account.analytic.account'].search([('cash_register_id','=',contract)])
        if contract:
            return {
                'control_code': contract.fcu_post(reciept,appcert),
            }
        return {
            'appcert': appcert,
            'contract': contract,
            'uid': uid,
            'context': context,
            'params': request.params,
#            'request.method': request.method,
#            'request.args': request.args,
            'post': post,
        }

# curl -H "Content-type:application/json" -X POST localhost:8069/fcu/kalle/add -d '{"method":"pluyy"}'|python -m json.tool
# openerp-server.conf:
#db_name = pos
#dbfilter = pos
#list_db = false

"""
https://www.skatteverket.se/rattsinformation/arkivforrattsligvagledning/foreskrifter/konsoliderade/2009/skvfs200912.5.2e56d4ba1202f950120800012422.html
http://www4.skatteverket.se/download/18.7d4d4f0515244e542f5a9fd/1453733397842/SKVFS+2009+2.pdf
http://www.skatteverket.se/download/18.76a43be412206334b89800012557/SKVFS+2009.03.pd
https://www.skatteverket.se/foretagochorganisationer/foretagare/kassaregister/anmalakassaregisterandringarochfel.4.69ef368911e1304a62580008748.html
Data    Beskrivning     Format
Datum och tid   Datum och klockslag för försäljning enligt 28 § c SKVFS 2009:1  12 siffror, format YYYYMMDDttmm
Organisationsnummer     Företagets organisationsnummer eller personnummer enligt 28 § a SKVFS 2009:1    10 siffror
Kassabeteckning     Kassabeteckning enligt 10 § SKVFS 2009:3    Maximalt 16 alfanumeriska tecken
Löpnummer   Löpnummer enligt 28 § d SKVFS 2009:1    Maximalt 12 siffror
Kvittotyp   Beroende av kvittotyp ska motsvarande text skapas:  Maximalt 6 alfanumeriska tecken
    - normal
    - kopia
    - ovning
    - profo
Returbelopp     Absolutvärde för summerat belopp returposter på ett kvitto  Maximalt 14 tecken inkl. decimalkomma*)
Försäljningsbelopp  Belopp för kunden att betala enligt 28 § h SKVFS 2009:1     Maximalt 14 tecken inkl. decimalkomma*)
Momssats 1; Momssumma 1     Första momssats i procent; Belopp första momssats enligt 28 § j SKVFS 2009:1    <Procentsats>;<Belopp> Procentsats: maximalt 5 tecken inkl. decimalkomma.*) Belopp: maximalt 14 tecken inkl. decimalkomma.*) Fältlängd: 20 tecken inkl. semikolon.
Momssats 2; Momssumma 2     Andra momssats i procent; Belopp andra momssats enligt 28 § j SKVFS 2009:1  Procentsats: maximalt 5 tecken inkl. decimalkomma.*) Belopp: maximalt 14 tecken inkl. decimalkomma.*) Fältlängd: 20 tecken inkl. semikolon.
Momssats 3; Momssumma 3     Tredje momssats i procent; Belopp tredje momssats enligt 28 § j SKVFS 2009:1    <Procentsats>;<Belopp> Procentsats: maximalt 5 tecken inkl. decimalkomma.*) Belopp: maximalt 14 tecken inkl. decimalkomma.*) Fältlängd: 20 tecken inkl. semikolon.
Momssats 4; Momssumma 4     Fjärde momssats i procent; Belopp fjärde momssats enligt 28 § j SKVFS 2009:1    <Procentsats>;<Belopp> Procentsats: maximalt 5 tecken inkl. decimalkomma.*) Belopp: maximalt 14 tecken inkl. decimalkomma.*) Fältlängd: 20 tecken inkl. semikolon.
*) Det ska alltid vara två siffror efter decimalkommat


5 §    Data ska vara i ASCII teckenformat och högerjusterad, eventuellt ifylld med blanka tecken (mellanslag) för att uppnå angiven fältlängd.
"""


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    cash_register_id = fields.Char()
    app_id = fields.Char()

    def fcu_post(self,reciept,app_id):
        return "control_code"
