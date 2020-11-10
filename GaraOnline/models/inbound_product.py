from odoo import api, fields, models
from datetime import date
import string
import random
from odoo.exceptions import UserError


class InBoundProduct(models.Model):
    _name = 'inbound.product'

    name = fields.Char('Mã nhập')
    # currency_id = fields.Many2one('res.currency', string='Currency', compute='get_currency')
    in_bound_amount = fields.Integer('Số lượng nhập kho')
    payment_date = fields.Date('Payment date', default=date.today())
    product = fields.Many2one('product.template.card', string='Sản phẩm')
    notes = fields.Text('Notes')

    # @api.depends('booking')
    # def get_currency(self):
    #     for rec in self:
    #         rec.currency_id = self.env['res.currency'].search([('name', '=', 'VND')]).id

    def get_code(self, qty, product_default_code):
        size = 12
        chars = string.ascii_uppercase + string.digits
        list = []
        i = 0
        while i < int(qty):
            code = product_default_code + ''.join(random.choice(chars) for _ in range(size))
            if code not in list:
                list.append(code)
                i += 1
        return list

    @api.model
    def create(self, vals_list):
        res = super(InBoundProduct, self).create(vals_list)
        if res.in_bound_amount == 0:
            raise UserError('Số lượng nhập phải lớn hơn 0.')
        else:
            code = self.get_code(res.in_bound_amount, res.product.product_default_code)
            size = 12
            chars = string.ascii_uppercase + string.digits
            check = 0
            while check is not None:
                if not code:
                    break
                else:
                    if len(code) > 1:
                        query = '''SELECT code FROM product_product_card as ppc WHERE ppc.code IN %s '''
                        self._cr.execute(query % (tuple(code),))
                    else:
                        query = '''SELECT code FROM product_product_card as ppc WHERE ppc.code = '%s' '''
                        self._cr.execute(query % (code[0],))
                    check = self._cr.fetchall()
                    if not check:
                        list = []
                        for rec in code:
                            dict_val = {}
                            dict_val['code'] = rec
                            dict_val['product'] = res.product.id
                            list.append(dict_val)
                        self.env['product.product.card'].create(tuple(list))
                        break
                    else:
                        for rec in check:
                            code.remove(rec[0])
                            code_again = res.product_default_code + ''.join(random.choice(chars) for _ in range(size))
                            if code_again not in code:
                                code.append(code_again)
            return res

    # def create_inbound_payment(self):
    #     # self.loyalty_id.time_active = self.payment_date
    #     self.env['inbound.product'].create({
    #         'name': self.name,
    #         'payment_date': self.payment_date,
    #         'in_bound_amount': self.in_bound_amount,
    #         'product': self.product.id,
    #         'notes': self.notes,
    #     })

