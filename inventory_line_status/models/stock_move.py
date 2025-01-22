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
            
            # Check if all lines have same status and update move
            if line.move_id:
                all_lines = line.move_id.move_line_ids
                if all_lines and all(l.check_status == new_status for l in all_lines):
                    self.env.cr.execute("""
                        UPDATE stock_move 
                        SET check_status = %s 
                        WHERE id = %s
                    """, (new_status, line.move_id.id))
        return True

    @api.model
    def create(self, vals):
        if vals.get('move_id') and 'check_status' not in vals:
            move = self.env['stock.move'].browse(vals['move_id'])
            if move.check_status:  # Only copy if parent has non-NULL status
                vals['check_status'] = move.check_status
        return super(StockMoveLine, self).create(vals)
