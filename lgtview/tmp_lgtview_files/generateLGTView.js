Ext.regModel('Metadata', {
    fields: [
        {type: 'string', name: 'name'}
    ]
});

var ds = [
    {"name": "euk_genus"},
    {"name": "euk_length"},
    {"name": "bac_genus"}
]

var store = Ext.create('Ext.data.Store', {
    model: 'Metadata',
    data: ds
});

Ext.onReady(function(){

    // Path to script to populate the form with relevant info
    var EXTRACT_METADATA_URL = '/cgi-bin/extractLoadingData.cgi'; 


    var pie_combo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select metadata',
        multiSelect: true,
        displayField: 'name',
        store: store,
        queryMode: 'local'
    });

    var filter_combo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Filter',
        multiSelect: false,
        displayField: 'name',
        store: store
    });

    var filter_combo2 = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Operator',
        multiSelect: false,
        displayField: 'name',
        store: store
    });

    var middlepanel = Ext.create('Ext.panel.Panel', ({
        region: 'center',
        title: 'Pie Graph Configuration',
        flex: 1,
        items: [pie_combo]
    }));

    var bottompanel = Ext.create('Ext.panel.Panel', ({
        autoScroll: true,
        region: 'south',
        title: 'Filter Configuration',
        flex: 1,
        layout: 'hbox',
        items: [filter_combo, filter_combo2]
    }));

    var submitSRA = Ext.create('Ext.Button', {
        text: 'Extract Metadata',
        bodyPadding: 20,
        width: 100,
        style: { marginLeft: '15px' }
    });

    var form = Ext.create('Ext.form.field.Text', ({
        bodyPadding: 10,
        width: 370,
        labelWidth: 160,
        fieldLabel: 'Sequence Read Archive ID',
    }));
    
    var toppanel =  Ext.create('Ext.panel.Panel', ({
        frame: true,
        region: 'north',
        title: 'LGTView Generator',
        defaultType: 'textfield',
        layout: {
            type: 'hbox',
            pack: 'center'
        },
        items: [form,submitSRA]
    }));

    var lastpanel =  Ext.create('Ext.panel.Panel', ({
        frame: true,
        region: 'south',
        layout: {
            type: 'hbox',
            pack: 'center'
        },
        items: [{
            xtype: 'button',
            text: 'Load LGTView'
        }]
    }));

    var vp = new Ext.Viewport({
        layout: 'border',
        autoScroll: true,
        defaults: {split: true},
        items: [toppanel,middlepanel,bottompanel,lastpanel]
    });
    
    vp.doLayout();
});
