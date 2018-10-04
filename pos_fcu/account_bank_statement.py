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


import logging
import simplejson
import os
import openerp
import time
import random
import werkzeug.utils

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import module_boot, login_redirect

_logger = logging.getLogger(__name__)


class PosController(http.Controller):

    @http.route('/pos_fcu/init', type="json", auth="none")
    def init(self):
        registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
        notifications = registry['im_chat.message'].init_messages(cr, uid, context=context)
        return notifications

    @http.route('/pos_fcu/post', type="json", auth="none")
    def post(self, uuid, message_type, message_content):
        registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
        # execute the post method as SUPERUSER_ID
        message_id = registry["im_chat.message"].post(cr, openerp.SUPERUSER_ID, uid, uuid, message_type, message_content, context=context)
        return message_id


class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'journal_user': fields.boolean('PoS Payment Method', help="Check this box if this journal define a payment method that can be used in point of sales."),

        'amount_authorized_diff' : fields.float('Amount Authorized Difference', help="This field depicts the maximum difference allowed between the ending balance and the theorical cash when closing a session, for non-POS managers. If this maximum is reached, the user will have an error message at the closing of his session saying that he needs to contact his manager."),
        'self_checkout_payment_method' : fields.boolean('Self Checkout Payment Method'), #FIXME : this field is obsolete
    }
    _defaults = {
        'self_checkout_payment_method' : False,
    }


class account_cash_statement(osv.osv):
    _inherit = 'account.bank.statement'
    _columns = {
        'pos_session_id' : fields.many2one('pos.session', copy=False),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
