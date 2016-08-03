var ds = Ext.create('Ext.data.Store', {
    fields: ['name', 'filter', 'pie', 'id', 'operator'],
    data: [
    {"name": "euk_genus1", "filter": false, "pie": false, "id": "euk_genus1", "operator" : 'matches'},
    {"name": "euk_genus2", "filter": false, "pie": false, "id": "euk_genus2", "operator" : 'matches'},
    {"name": "euk_genus3", "filter": false, "pie": false, "id": "euk_genus3", "operator" : 'matches'}
    ]
});

Ext.Loader.setConfig({
    enabled: true,
    paths: {
        'Ext.ux': 'ux/'
    }
});

Ext.require('Ext.ux.CheckColumn');

Ext.onReady(function(){

    // Path to script to populate the form with relevant info
    var EXTRACT_METADATA_URL = '/cgi-bin/extractLoadingData.cgi'; 

    var grid = Ext.create('Ext.grid.Panel', {
        store: ds,
        columns: [
            {
            xtype: 'checkcolumn',
            text: 'Pie Graph',
            dataIndex: 'pie',
            id: 'pie',
            align: 'center',
            listeners: {
                'checkchange': function(col, idx, isChecked) {
                    var rec = grid.store.getAt(idx);
                    rec.set("filter", false);
                }
            }
            },
            {
            xtype: 'checkcolumn',
            text: 'Filter',
            dataIndex: 'filter',
            align: 'center',
            listeners: {
                'checkchange': function(col, idx, isChecked) {
                    var rec = grid.store.getAt(idx);
                    rec.set("pie", false);
                }
            }
            },
            {text: "Metadata", width: 150, dataIndex: 'name', flex: 1},
            {
            text: "Comparison Operator", 
            width: 150, 
            dataIndex: 'operator',
            align: 'center',
            listeners: {
                cellclick: function(record, tr, rowIndex, e, eOpts){
                    alert('hi');
                    var rec = grid.store.getAt(rowIndex);
                    rec.set("operator", "<");
                }
            }
            }
        ],
        columnLines: true,
        frame: true,
        title: 'Configure Pie Graphs and Filters'
    });

    var middlepanel = Ext.create('Ext.panel.Panel', ({
        region: 'center',
        flex: 1,
        items: [grid]
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
        items: [toppanel,middlepanel,lastpanel]
    });
    
    vp.doLayout();
});