// odoo.define('dynamic_report.DashboardRewrite', function (require) {
//     "use strict";
    
//     const ActionMenus = require('web.ActionMenus');
//     const ComparisonMenu = require('web.ComparisonMenu');
//     const ActionModel = require('web/static/src/js/views/action_model.js');
//     const FavoriteMenu = require('web.FavoriteMenu');
//     const FilterMenu = require('web.FilterMenu');
//     const GroupByMenu = require('web.GroupByMenu');
//     const patchMixin = require('web.patchMixin');
//     const Pager = require('web.Pager');
//     const SearchBar = require('web.SearchBar');
//     const { useModel } = require('web/static/src/js/model.js');
    
//     const { Component, hooks } = owl;
    
//     var concurrency = require('web.concurrency');
//     var config = require('web.config');
//     var field_utils = require('web.field_utils');
//     var time = require('web.time');
//     var utils = require('web.utils');
//     var AbstractAction = require('web.AbstractAction');
//     var ajax = require('web.ajax');
//     var Dialog = require('web.Dialog');
//     var field_utils = require('web.field_utils');
//     var core = require('web.core');
//     var rpc = require('web.rpc');
//     var session = require('web.session');
//     var web_client = require('web.web_client');
//     var abstractView = require('web.AbstractView');
//     var _t = core._t;
//     var QWeb = core.qweb;
    
//     const { useRef, useSubEnv } = hooks;

//     var HrDashboard = AbstractAction.extend({
    
//         template: 'RptDashboardMain',
    
//         init: function(parent, context) {
//             this._super(parent, context);
//         },
    
//         willStart: function(){
//             var self = this;
//             this.login_employee = {};
//             return this._super()
//         },
    
//         start: function() {
//             console.log("START FUNCTION")
//             var self = this;
//             this.set("title", 'Dashboard');
//             return this._super().then(function() {
//                 self.render_dashboards();
                
//                 self.$el.parent().addClass('oe_background_grey');
//             });
//         },
    
    
//         render_dashboards: function() {
//             var self = this;
            
//             self.$('.o_hr_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));

//         },

//        });
    
//         core.action_registry.add('rpt_dashboard', HrDashboard);
    
//     return HrDashboard;
    
//     });

odoo.define('custom_dashboard.dashboard_action', function (require){
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var CustomDashBoard = AbstractAction.extend({
      template: 'CustomDashBoard',
      
         start: function() {
               console.log("START FUNCTION")
               var self = this;
               this.set("title", 'Dashboard');
               return this._super().then(function() {
                  self.render_dashboards();
                  
                  self.$el.parent().addClass('oe_background_grey');
               });
         },
      
         render_dashboards: function() {
               var self = this;
               
               self.$('.o_hr_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));

         },
      })
   core.action_registry.add('custom_dashboard_tags', CustomDashBoard);
   return CustomDashBoard;
   })