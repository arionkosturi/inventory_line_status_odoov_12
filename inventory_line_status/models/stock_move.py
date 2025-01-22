from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    # Add prefetch hints for commonly accessed fields
    _prefetch_fields = ['move_line_ids', 'check_status']

    check_status = fields.Selection([
        ('checked', '✓'),
        ('unchecked', '⚠')
    ], string='Status', default='unchecked', copy=False, index=True)

    def toggle_status(self):
        # Prefetch in batches for better performance
        self.mapped('move_line_ids.check_status')
        
        # Prepare bulk updates
        new_status_by_id = {
            move.id: 'checked' if move.check_status == 'unchecked' else 'unchecked'
            for move in self
        }
        
        # Group records by new status for fewer writes
        moves_by_status = {}
        lines_by_status = {}
        
        for move in self:
            new_status = new_status_by_id[move.id]
            moves_by_status.setdefault(new_status, self.env['stock.move'])
            moves_by_status[new_status] |= move
            
            if move.move_line_ids:
                lines_by_status.setdefault(new_status, self.env['stock.move.line'])
                lines_by_status[new_status] |= move.move_line_ids

        # Perform bulk updates by status
        for status, moves in moves_by_status.items():
            moves.write({'check_status': status})
        
        for status, lines in lines_by_status.items():
            lines.write({'check_status': status})
            
        return True

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # Optimize searches on check_status
        if args and any(arg[0] == 'check_status' for arg in args):
            return super()._search(args, offset=offset, limit=limit, order=order, 
                                 count=count, access_rights_uid=access_rights_uid)
        return super()._search(args, offset=offset, limit=limit, order=order,
                             count=count, access_rights_uid=access_rights_uid)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Add prefetch hints
    _prefetch_fields = ['move_id', 'check_status']

    check_status = fields.Selection([
        ('checked', '✓'),
        ('unchecked', '⚠')
    ], string='Status', default='unchecked', copy=False, index=True)

    def toggle_status(self):
        # Prefetch all related records at once
        moves = self.mapped('move_id')
        moves.mapped('move_line_ids.check_status')
        
        # Group by current status for efficient toggling
        to_check = self.filtered(lambda l: l.check_status == 'unchecked')
        to_uncheck = self - to_check
        
        # Perform updates in batches
        if to_check:
            to_check.write({'check_status': 'checked'})
        if to_uncheck:
            to_uncheck.write({'check_status': 'unchecked'})

        # Update parent moves efficiently
        for move in moves:
            move_lines = move.move_line_ids
            if move_lines:
                statuses = set(move_lines.mapped('check_status'))
                if len(statuses) == 1:
                    move.check_status = statuses.pop()
        
        return True

    @api.model_create_multi
    def create(self, vals_list):
        # Group by move_id for efficient status fetching
        moves_to_fetch = {
            vals['move_id'] for vals in vals_list 
            if vals.get('move_id') and not vals.get('check_status')
        }
        
        # Prefetch move statuses in one query
        moves_dict = {}
        if moves_to_fetch:
            moves = self.env['stock.move'].browse(list(moves_to_fetch))
            moves_dict = {move.id: move.check_status for move in moves}
        
        # Update vals efficiently
        for vals in vals_list:
            if vals.get('move_id') and not vals.get('check_status'):
                vals['check_status'] = moves_dict.get(vals['move_id'], 'unchecked')
        
        return super().create(vals_list)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # Optimize searches on check_status
        if args and any(arg[0] == 'check_status' for arg in args):
            return super()._search(args, offset=offset, limit=limit, order=order,
                                 count=count, access_rights_uid=access_rights_uid)
        return super()._search(args, offset=offset, limit=limit, order=order,
                             count=count, access_rights_uid=access_rights_uid)
