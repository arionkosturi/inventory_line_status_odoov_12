# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_bulk_initialize_status(self):
        """Initialize all unprocessed lines to unchecked status"""
        for picking in self:
            picking.move_lines.set_all_null_to_unchecked()
        return True

    def action_bulk_toggle_status(self):
        """Toggle status for all move lines"""
        for picking in self:
            picking.move_lines.toggle_status()
        return True
