odoo.define('smart_serial_inbound.serial_scanner', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const viewRegistry = require('web.view_registry');
    const FormView = require('web.FormView');

    const SerialFormController = FormController.extend({
        events: _.extend({}, FormController.prototype.events, {
            'keypress input[name="last_scanned"]': '_onScanSerial',
        }),

        _onScanSerial: function (event) {
            if (event.which === 13) { // Enter key
                this._updateField('last_scanned', event.target.value);
                event.target.value = '';
            }
        }
    });

    const SerialFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: SerialFormController,
        }),
    });

    viewRegistry.add('serial_form_view', SerialFormView);
});
