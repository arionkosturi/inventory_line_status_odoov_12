odoo.define('inventory_line_status.status_handler', function (require) {
    "use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var FormController = require('web.FormController');
    var ActionManager = require('web.ActionManager');

    // Handle status updates in list view
    ListController.include({
        custom_events: _.extend({}, ListController.prototype.custom_events, {
            reload_status: '_onReloadStatus',
        }),

        _onReloadStatus: function (ev) {
            var self = this;
            var data = ev.data.params;
            
            // Update single move
            if (data.move_id) {
                this._updateRecord(data.move_id, data.status);
                if (data.move_line_ids) {
                    data.move_line_ids.forEach(function(line_id) {
                        self._updateRecord(line_id, data.status);
                    });
                }
            }
            
            // Update multiple moves
            if (data.move_ids) {
                data.move_ids.forEach(function(move_id) {
                    self._updateRecord(move_id, data.status);
                });
            }
        },

        _updateRecord: function (id, status) {
            var record = this.model.get(id);
            if (record) {
                record.data.check_status = status;
                this.renderer.updateRecord(record);
            }
        }
    });

    // Handle status updates in form view
    FormController.include({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            reload_status: '_onReloadStatus',
        }),

        _onReloadStatus: function (ev) {
            var self = this;
            var data = ev.data.params;
            
            if (data.move_id) {
                this._updateRecord('stock.move', data.move_id, data.status);
            }
            if (data.move_line_id) {
                this._updateRecord('stock.move.line', data.move_line_id, data.status);
            }
        },

        _updateRecord: function (model, id, status) {
            var record = this.model.get(id);
            if (record) {
                record.data.check_status = status;
                this.renderer.updateRecord(record);
            }
        }
    });

    // Register client action
    core.action_registry.add('reload_status', function(parent, action) {
        parent.trigger_up('reload_status', action);
        return $.when();
    });
});
