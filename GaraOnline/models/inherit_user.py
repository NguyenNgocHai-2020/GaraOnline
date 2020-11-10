from odoo import api, fields, models


class InheritResUsers(models.Model):
    _inherit = 'res.users'

    regency = fields.Selection(selection=[('collaborators', 'CTV'), ('agency', 'Đại lý')], string='Hình thức')
    product_template_ids = fields.Many2many(comodel_name="product.template.card", string="Sản phẩm")
    amount_received = fields.Integer('Số lượng nhận', compute='_calculate_amount_received')
    product_amount_used = fields.Integer('Số lượng đã kích hoạt', compute='_calculate_amount_used')
    product_product_ids = fields.One2many('product.product.card', 'users_ids', string='Biến thể')
    commission_total = fields.Float(compute='_calculate_commission_total', string='Tổng tiền hoa hồng', store=True)

    @api.depends('product_product_ids')
    def _calculate_amount_received(self):
        if self.product_product_ids:
            self.amount_received = len(self.product_product_ids)

    @api.depends('product_product_ids')
    def _calculate_amount_used(self):
        if self.product_product_ids:
            count = 0
            for rec in self.product_product_ids:
                if rec.state == 'sold':
                    count += 1
            self.product_amount_used = count

    @api.depends('product_product_ids')
    def _calculate_commission_total(self):
        for user in self:
            if user.product_product_ids:
                total = 0
                for rec in user.product_product_ids:
                    if rec.state == 'sold':
                        total += rec.commission
                user.commission_total = total

