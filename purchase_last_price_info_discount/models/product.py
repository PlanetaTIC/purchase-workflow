# Copyright 2020 PlanetaTIC <info@planetatic.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def set_product_last_purchase(self, order_id=False):
        """ Get last purchase price, last purchase date and last supplier """
        PurchaseOrderLine = self.env['purchase.order.line']
        if not self.check_access_rights('write', raise_exception=False):
            return
        for product in self:
            date_order = False
            price_unit = 0.0
            last_supplier = False

            # Check if Order ID was passed, to speed up the search
            if order_id:
                lines = PurchaseOrderLine.search([
                    ('order_id', '=', order_id),
                    ('product_id', '=', product.id)], limit=1)
            else:
                lines = PurchaseOrderLine.search(
                    [('product_id', '=', product.id),
                     ('state', 'in', ['purchase', 'done'])]).sorted(
                    key=lambda l: l.order_id.date_order, reverse=True)

            if lines:
                # Get most recent Purchase Order Line
                last_line = lines[:1]

                date_order = last_line.order_id.date_order
                # Compute Price Unit in the Product base UoM
                price_unit = last_line._get_discounted_price_unit()
                last_supplier = last_line.order_id.partner_id

            # Assign values to record
            product.write({
                "last_purchase_date": date_order,
                "last_purchase_price": price_unit,
                "last_supplier_id": last_supplier.id
                if last_supplier else False,
            })
            # Set related product template values
            product.product_tmpl_id.set_product_template_last_purchase(
                date_order, price_unit, last_supplier)
