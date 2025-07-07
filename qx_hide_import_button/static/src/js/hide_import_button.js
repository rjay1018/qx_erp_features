odoo.define('hide_import_button.hide_import_button', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({
        renderButtons: function ($node) {
            this._super($node);
            var self = this;
            this._rpc({
                model: 'res.users',
                method: 'has_group',
                args: ['hide_import_button.group_no_import'],
            }).then(function (inGroup) {
                if (inGroup && self.$buttons) {
                    self.$buttons.find('.o_list_button_import').remove();
                }
            });
        },
    });
});
