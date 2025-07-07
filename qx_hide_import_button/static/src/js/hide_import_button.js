odoo.define('qx_hide_import_button.hide_import_button', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({
        renderButtons: function ($node) {
            this._super($node);

            console.log("✅ JS Loaded: Checking user group...");

            var self = this;
            this._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['qx_hide_import_button.group_no_import'],
            }).then(function (inGroup) {
                console.log("✅ User in restricted group?", inGroup);
                if (inGroup && self.$buttons) {
                    console.log("❌ Hiding Import Button");
                    self.$buttons.find('.o_list_button_import').remove();
                }
            });
        },
    });
});
