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
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    pos_order_ids = fields.One2many(comodel_name='pos.order', inverse_name='partner_id', string='POS Order')

    @api.one
    def _pos_order_sum(self):
        self.pos_order_sum = sum([o.amount_total - o.amount_tax for o in self.pos_order_ids])
    pos_order_sum = fields.Float(compute='_pos_order_sum',string='Sum')

    @api.model
    #~ @api.returns('self', lambda value: value.id)
    def create(self, vals):

        pos_customer = False
        if 'post_customer' in vals:
            del vals['post_customer']
            pos_customer = True
        partner = super(res_partner, self).create(vals)
        if pos_customer:
            partner.write({'category_id': [(6, 0 , [self.env.ref('pos_partner.categ_pos_customer').id])]})

        return partner

#~ class pos_session_opening(models.TransientModel):
    #~ _inherit = 'pos.session.opening'

    #~ @api.multi
    #~ def open_ui(self):
        #~ request.session['pos_customer'] = 1
        #~ return super(pos_session_opening, self).open_ui()
