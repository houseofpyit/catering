odoo.define('catering.form', function (require){
    "use strict";
    // require original module JS
    var BasicController = require('web.BasicController');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var dialogs = require('web.view_dialogs');

    var _t = core._t;
    var qweb = core.qweb;
    var FormController = require('web.FormController');
    
    // Extend widget
    FormController.include({
        renderButtons: function ($node) {
            var $footer = this.footerToButtons ? this.renderer.$el && this.renderer.$('footer') : null;
            var mustRenderFooterButtons = $footer && $footer.length;
            if ((this.defaultButtons && !this.$buttons) || mustRenderFooterButtons) {
                this.$buttons = $('<div id="myDiv" style="display: flex;justify-content: center;align-items: center;position: absolute;bottom: 0;left: 0;z-index: 10;right: 0;background-color: #fff;padding: 10px;"></div>');             
                // console.log('this.$buttons:::::::::::::',this.$buttons.length,$footer)
                if (mustRenderFooterButtons) {
                    this.$buttons.append($footer);
                } else {
                    this.$buttons.append(qweb.render("FormView.buttons", {widget: this}));
                    this.$buttons.on('click', '.o_form_button_edit', this._onEdit.bind(this));
                    this.$buttons.on('click', '.o_form_button_create', this._onCreate.bind(this));
                    this.$buttons.on('click', '.o_form_button_save', this._onSave.bind(this));
                    this.$buttons.on('click', '.o_form_button_cancel', this._onDiscard.bind(this));
                    this._assignSaveCancelKeyboardBehavior(this.$buttons.find('.o_form_buttons_edit'));
                    this.$buttons.find('.o_form_buttons_edit').tooltip({
                        delay: {show: 200, hide:0},
                        title: function(){
                            return qweb.render('SaveCancelButton.tooltip');
                        },
                        trigger: 'manual',
                    });
                }
            }
            if (this.$buttons && $node) {
                this.$buttons.appendTo($node);
            }
            
            // setTimeout(() => {
            //     this.$buttons.appendTo($node);
            //     this.$buttons.appendTo($(document.body));
            // }, 100);
        },
        
    });
    
    return FormController;
});

// For List View
odoo.define('list_controller_inherited', function (require) {
    'use strict';

    var ListController = require('web.ListController');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    ListController.include({
        renderButtons: function ($node) {
            if (this.noLeaf || !this.hasButtons) {
                this.hasButtons = false;
                this.$buttons = $('<div>');
            } else {
                this.$buttons = $('<div id="myDiv" style="display: flex;justify-content: center;align-items: center;position: absolute;bottom: 0;left: 0;z-index: 10;right: 0;background-color: #fff;padding: 10px;"></div>');             
                this.$buttons.append(qweb.render(this.buttons_template, {widget: this}));
                this.$buttons.on('click', '.o_list_button_add', this._onCreateRecord.bind(this));
                this._assignCreateKeyboardBehavior(this.$buttons.find('.o_list_button_add'));
                this.$buttons.find('.o_list_button_add').tooltip({
                    delay: {show: 200, hide: 0},
                    title: function () {
                        return qweb.render('CreateButton.tooltip');
                    },
                    trigger: 'manual',
                });
                this.$buttons.on('mousedown', '.o_list_button_discard', this._onDiscardMousedown.bind(this));
                this.$buttons.on('click', '.o_list_button_discard', this._onDiscard.bind(this));
            }
            if ($node) {
                this.$buttons.appendTo($node);
            }
        },
    });

    return ListController;
});

// For Kanban View
odoo.define('kanban_controller_inherited', function (require) {
    'use strict';

    var KanbanController = require('web.KanbanController');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    KanbanController.include({
        renderButtons: function ($node) {
            if (!this.hasButtons || !this.is_action_enabled('create')) {
                return;
            }
            this.$buttons = $('<div id="myDiv" style="display: flex;justify-content: center;align-items: center;position: absolute;bottom: 0;left: 0;z-index: 10;right: 0;background-color: #fff;padding: 10px;"></div>');             
    
            this.$buttons.append(qweb.render(this.buttons_template, {
                btnClass: 'btn-primary',
                widget: this,
            }));
            this.$buttons.on('click', 'button.o-kanban-button-new', this._onButtonNew.bind(this));
            this.$buttons.on('keydown', this._onButtonsKeyDown.bind(this));
            if ($node) {
                this.$buttons.appendTo($node);
            }
        },
    });

    return KanbanController;
});
