from odoo import api, fields, models


class SaleManage(models.Model):
    _name = 'sale.manage'

    user = fields.Many2one(comodel_name='res.users')
    product_variants = fields.Many2one(comodel_name='product.product.card')
    name = fields.Char(related='user.name', string='Tên')
    regency = fields.Selection(related='user.regency', string='Loại hình')
    # product_template = fields.Char(related='product_variants.name', string='Sản phẩm')
    amount_received = fields.Integer(related='user.amount_received', string='Số sản phẩm nhận')
    product_amount_used = fields.Integer(related='user.amount_received', string='Số sản phẩm đã bán được')