odoo.define('ct_contact_v15.custome_group', function(require) {
    "use strict";

    var ListView = require('web.ListView');
    console.log("-------------- call -----")
    ListView.include({
        _renderGroupByDropdown: function () {
            this._super.apply(this, arguments);

            // Hide the CustomGroupByItem template
            var $customGroupByItem = this.$('.o_add_custom_group_menu');
            $customGroupByItem.hide();
        },
    });
    // var SearchView = require('web.SearchView');

    // SearchView.include({
    //     init: function () {
    //         this._super.apply(this, arguments);
    //         this.customGroupByItems = this.customGroupByItems.filter(function (item) {
    //             return item.widget !== 'web.CustomGroupByItem';
    //         });
    //     },
    // });
});


// odoo.define('ct_contact_v15.custom_search_filters', function (require) {
//     'use strict';

//     var SearchFilters = require('web.SearchFilters');

//     SearchFilters.include({
//         /**
//          * @override
//          */
//         _renderGroupBys: function () {
//             this._super.apply(this, arguments);

//             // Remove CustomGroupByItem
//             this.$('.o_searchview_groupbys_items .o_dropdown_menu .o_custom_groupby_item').remove();
//         },
//     });
// });
