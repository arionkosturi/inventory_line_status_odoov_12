from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def set_all_null_to_unchecked(self):
        # Get all moves with NULL status
        moves = self.mapped('move_ids_without_package').filtered(lambda m: not m.check_status)
        if moves:
            moves.set_all_null_to_unchecked()
        return True
