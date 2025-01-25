from odoo import models, fields, api
from odoo.tools import float_compare
import logging
import psycopg2

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    check_status = fields.Selection([
        ('unchecked', 'Unchecked'),
        ('checked', 'Checked')
    ], string='Check Status', copy=False)

    toggle_button = fields.Char(compute='_compute_toggle_button', string=' ')
    
    @api.multi
    def _compute_toggle_button(self):
        for move in self:
            move.toggle_button = move.check_status or 'unprocessed'

    def _get_next_status(self, current_status):
        """Helper method to determine the next status in the cycle."""
        if not current_status:
            return 'unchecked'
        elif current_status == 'unchecked':
            return 'checked'
        else:
            return 'unchecked'

    def toggle_status(self):
        """Toggle the check status with immediate UI update."""
        self.ensure_one()
        next_status = self._get_next_status(self.check_status)
        
        # Update status directly in database for speed
        self.env.cr.execute("""
            UPDATE stock_move
            SET check_status = %s
            WHERE id = %s
            RETURNING id
        """, (next_status, self.id))
        
        # Update related move lines in a single query
        if self.move_line_ids:
            self.env.cr.execute("""
                UPDATE stock_move_line
                SET check_status = %s
                WHERE move_id = %s
            """, (next_status, self.id))

        # Return data for client-side update
        return {
            'type': 'ir.actions.client',
            'tag': 'reload_status',
            'params': {
                'move_id': self.id,
                'status': next_status,
                'move_line_ids': self.move_line_ids.ids
            }
        }

    def action_bulk_toggle_status(self):
        """Bulk toggle status with optimized database operations."""
        if not self:
            return True

        # Get IDs of moves to update
        move_ids = self.filtered(lambda m: m.check_status != 'checked').ids
        if not move_ids:
            return True

        # Update moves in a single query
        self.env.cr.execute("""
            UPDATE stock_move
            SET check_status = 'checked'
            WHERE id = ANY(%s)
        """, (move_ids,))

        # Update related move lines in a single query
        self.env.cr.execute("""
            UPDATE stock_move_line
            SET check_status = 'checked'
            WHERE move_id = ANY(%s)
        """, (move_ids,))

        return {
            'type': 'ir.actions.client',
            'tag': 'reload_status',
            'params': {
                'move_ids': move_ids,
                'status': 'checked'
            }
        }

    def action_bulk_initialize_status(self):
        """Initialize all null status lines with optimized database operations."""
        if not self:
            return True

        # Get IDs of moves to update
        move_ids = self.filtered(lambda m: not m.check_status).ids
        if not move_ids:
            return True

        # Update moves in a single query
        self.env.cr.execute("""
            UPDATE stock_move
            SET check_status = 'unchecked'
            WHERE id = ANY(%s)
            AND check_status IS NULL
        """, (move_ids,))

        # Update related move lines in a single query
        self.env.cr.execute("""
            UPDATE stock_move_line
            SET check_status = 'unchecked'
            WHERE move_id = ANY(%s)
            AND check_status IS NULL
        """, (move_ids,))

        return {
            'type': 'ir.actions.client',
            'tag': 'reload_status',
            'params': {
                'move_ids': move_ids,
                'status': 'unchecked'
            }
        }

    def write(self, vals):
        """Override write to handle optimistic updates."""
        if 'check_status' in vals and not self.env.context.get('skip_optimistic'):
            try:
                # For bulk updates, we'll still use optimistic updates
                for move in self:
                    self.env.cr.execute("""
                        INSERT INTO stock_move_status_updates (move_id, new_status, create_date)
                        VALUES (%s, %s, now())
                        ON CONFLICT (move_id) DO UPDATE
                        SET new_status = EXCLUDED.new_status,
                            create_date = EXCLUDED.create_date
                    """, (move.id, vals['check_status']))
                return True
            except psycopg2.Error as e:
                _logger.warning("Failed to queue bulk status update: %s", str(e))
                # Fall back to normal write if async fails
                return super(StockMove, self).write(vals)
        return super(StockMove, self).write(vals)

    @api.model
    def process_pending_status_updates(self):
        """Process pending status updates in the background."""
        try:
            self.env.cr.execute("""
                WITH pending_updates AS (
                    DELETE FROM stock_move_status_updates
                    WHERE create_date < now() - interval '5 minutes'
                    RETURNING move_id, new_status
                )
                SELECT move_id, new_status FROM pending_updates
            """)
            updates = self.env.cr.fetchall()
            
            for move_id, new_status in updates:
                try:
                    move = self.browse(move_id)
                    if move.exists():
                        move.with_context(skip_optimistic=True).write({
                            'check_status': new_status
                        })
                    self.env.cr.commit()
                except Exception as e:
                    _logger.error(f"Failed to process status update for move {move_id}: {str(e)}")
                    self.env.cr.rollback()

        except psycopg2.Error as e:
            _logger.error("Failed to process status updates: %s", str(e))

        return True

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    check_status = fields.Selection([
        ('unchecked', 'Unchecked'),
        ('checked', 'Checked')
    ], string='Check Status', copy=False)

    def toggle_status(self):
        """Toggle status with optimized database operations."""
        self.ensure_one()
        move = self.move_id
        next_status = self.env['stock.move']._get_next_status(self.check_status)

        # Update line status directly in database
        self.env.cr.execute("""
            UPDATE stock_move_line
            SET check_status = %s
            WHERE id = %s
        """, (next_status, self.id))

        # Update parent move if all lines have same status
        if move:
            self.env.cr.execute("""
                UPDATE stock_move m
                SET check_status = %s
                WHERE id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM stock_move_line
                    WHERE move_id = m.id
                    AND (check_status IS NULL OR check_status != %s)
                )
            """, (next_status, move.id, next_status))

        return {
            'type': 'ir.actions.client',
            'tag': 'reload_status',
            'params': {
                'move_line_id': self.id,
                'move_id': move.id if move else False,
                'status': next_status
            }
        }

    @api.model
    def create(self, vals):
        """Inherit status from parent move when creating new lines"""
        if vals.get('move_id') and 'check_status' not in vals:
            move = self.env['stock.move'].browse(vals['move_id'])
            if move.check_status:  # Only copy if parent has non-NULL status
                vals['check_status'] = move.check_status
        return super().create(vals)
