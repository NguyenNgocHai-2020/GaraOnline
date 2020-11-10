from odoo import api, fields, models
import string
import random
from odoo.exceptions import UserError
import base64
import io
import qrcode


class ProductTemplateCard(models.Model):
    _name = 'product.template.card'

    def get_code_for_product_default_code(self):
        size = 5
        chars = string.ascii_uppercase + string.digits
        check = 0
        while check is not None:
            code = ''.join(random.choice(chars) for _ in range(size))
            query = '''SELECT product_default_code FROM product_template_card as ptc WHERE ptc.product_default_code LIKE '%s' '''
            self._cr.execute(query % (code,))
            check = self._cr.fetchall()
            if not check:
                break
        return code

    name = fields.Char('Tên sản phẩm')
    product_default_code = fields.Char('Mã sản phẩm', default=get_code_for_product_default_code)
    qty_product_in_stock = fields.Integer('Tồn kho', compute='_calulate_qty_product_in_stock', store=True)
    amount = fields.Integer('Tông số sản phẩm', compute='_calulate_product_amount', store=True)
    # amount = fields.Integer('Tông số sản phẩm')
    price = fields.Float('Giá')
    product_variants = fields.One2many(comodel_name="product.product.card", inverse_name="product",
                                       string="Mã sản phẩm",
                                       required=False, )
    inbound_product_ids = fields.One2many('inbound.product', 'product', string='Nhập')
    users_ids = fields.Many2many('res.users', 'product_template_users_rel', string='Nhà phân phối')

    @api.depends('product_variants.state')
    def _calulate_qty_product_in_stock(self):
        for rec in self:
            if rec.product_variants:
                count = 0
                for variants in rec.product_variants:
                    if variants.state == 'available':
                        count += 1
                rec.qty_product_in_stock = count

    @api.depends('inbound_product_ids')
    def _calulate_product_amount(self):
        for rec in self:
            if rec.inbound_product_ids:
                for i in rec.inbound_product_ids:
                    rec.amount += i.in_bound_amount


class ProductProductCard(models.Model):
    _name = 'product.product.card'
    _rec_name = 'name'

    state = fields.Selection(selection=[('available', 'Available'), ('sold', 'Sole')], string='Trạng thái',
                             default='available')
    product = fields.Many2one(comodel_name="product.template.card", string="Sản phẩm", required=False)
    name = fields.Char(related='product.name', string='Tên sản phẩm', track_visibility='always')
    price = fields.Float(related='product.price', string='Giá', track_visibility='always')
    commission = fields.Float(compute='_calculate_commission', string='Tiền hoa hồng', store=True)
    code = fields.Text('Mã')
    qr_code = fields.Binary('QR Code', compute="_generate_qr_code")
    users_ids = fields.Many2one('res.users', string='Nhà phân phối')
    # regency = fields.Selection(related='users_ids.regency')

    def sold_out_product_variants(self):
        self.state = 'sold'

    @api.depends('code')
    def _generate_qr_code(self):
        if self.code:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
            if self.id:
                qr.add_data('http://192.168.1.21:8080/web#id=' + str(
                    self.id) + '&action=556&model=res.users&view_type=form&menu_id=372')
                qr.make(fit=True)
                img = qr.make_image()
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                qrcode_img = base64.b64encode(buffer.getvalue())
                self.update({'qr_code': qrcode_img, })

    @api.depends('users_ids')
    def _calculate_commission(self):
        for product in self:
            if product.users_ids:
                for rec in product.users_ids:
                    if rec.regency == 'collaborators':
                        product.commission = product.price * 0.05
                    else:
                        product.commission = product.price * 0.1

