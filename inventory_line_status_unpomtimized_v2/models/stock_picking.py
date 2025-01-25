from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def set_all_null_to_unchecked(self):
        moves = self.mapped('move_ids_without_package').filtered(lambda m: not m.check_status)
        if moves:
            moves.write({'check_status': 'unchecked'})
            # Update related move lines
            self.env.cr.execute("""
                UPDATE stock_move_line
                SET check_status = 'unchecked'
                WHERE move_id IN %s
                AND check_status IS NULL
            """, (tuple(moves.ids),))
        return True
