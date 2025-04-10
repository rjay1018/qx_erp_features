odoo.define('custom_serial_update.barcode_scanner', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    const BarcodeScannerField = AbstractField.extend({
        template: 'BarcodeScannerField',
        events: {
            'keypress': '_onKeypress',
        },

        init() {
            this._super(...arguments);
            this.serials = [];
        },

        _onKeypress(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const scannedValue = this.$el.val().trim();
                if (scannedValue) {
                    this.serials.push(scannedValue);
                    this.$el.val(''); // Clear the input field
                    this._setValue(this.serials.join('\n'));
                }
            }
        },
    });

    fieldRegistry.add('barcode_scanner', BarcodeScannerField);
});