from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    check_status = fields.Selection([
        ('checked', '✓'),
        ('unchecked', '⚠')
    ], string='Status', copy=False)

    def toggle_status(self):
        for move in self:
            # Handle three-state toggle
            if not move.check_status:  # NULL -> unchecked
                new_status = 'unchecked'
            elif move.check_status == 'unchecked':  # unchecked -> checked
                new_status = 'checked'
            else:  # checked -> unchecked
                new_status = 'unchecked'
            
            # Update move lines in a single query
            if move.move_line_ids:
                self.env.cr.execute("""
                    UPDATE stock_move_line 
                    SET check_status = %s 
                    WHERE move_id = %s
                """, (new_status, move.id))
            move.check_status = new_status
        return True

    def set_all_null_to_unchecked(self):
        # Get all moves with NULL status
        moves = self.filtered(lambda m: not m.check_status)
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

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    check_status = fields.Selection([
        ('checked', '✓'),
        ('unchecked', '⚠')
    ], string='Status', copy=False)

    def toggle_status(self):
        for line in self:
            # Handle three-state toggle
            if not line.check_status:  # NULL -> unchecked
                new_status = 'unchecked'
            elif line.check_status == 'unchecked':  # unchecked -> checked
                new_status = 'checked'
            else:  # checked -> unchecked
                new_status = 'unchecked'
            
            line.check_status = new_status
            
            # Check if all lines have same status using EXISTS
            if line.move_id:
                self.env.cr.execute("""
                    UPDATE stock_move m
                    SET check_status = %s
                    WHERE id = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM stock_move_line
                        WHERE move_id = m.id
                        AND (check_status IS NULL OR check_status != %s)
                    )
                """, (new_status, line.move_id.id, new_status))
        return True

    @api.model
    def create(self, vals):
        if vals.get('move_id') and 'check_status' not in vals:
            move = self.env['stock.move'].browse(vals['move_id'])
            if move.check_status:  # Only copy if parent has non-NULL status
                vals['check_status'] = move.check_status
        return super().create(vals)
