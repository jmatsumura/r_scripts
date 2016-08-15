var ds = Ext.create('Ext.data.Store', {
    fields: ['name', 'filter', 'pie', 'id', 'operator'],
    data: [
    {"name": "euk_genus1", "filter": false, "pie": false, "id": "euk_genus1", "operator" : 'NA'},
    {"name": "euk_genus2", "filter": false, "pie": false, "id": "euk_genus2", "operator" : 'NA'},
    {"name": "euk_genus3", "filter": false, "pie": false, "id": "euk_genus3", "operator" : 'NA'}
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
    var EXTRACT_METADATA_URL = '/cgi-bin/build_metadata_table.cgi'; 

    var table = Ext.create('Ext.data.Store', {
        storeId:'table',
        fields: ['name', 'filter', 'pie', 'id', 'operator'],
        proxy: {
            type: 'ajax',
            url: EXTRACT_METADATA_URL,
            actionMethods: {
                read: 'POST'
            },
            reader: {
                type: 'json',
                root: 'root'
            }
        },
        autoLoad: false
    });

    var grid = Ext.create('Ext.grid.Panel', {
        store: table,
        selType: 'cellmodel',
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
                    rec.set("operator", 'NA');
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
                    if(rec.get("filter") === false) {
                        rec.set("operator", 'NA');
                    } else {
                        rec.set("operator", 'matches');
                    }
                }
            }
            },
            {text: "Metadata", width: 150, dataIndex: 'name', flex: 1},
            {
            text: "Comparison Operator", 
            width: 150, 
            dataIndex: 'operator',
            align: 'center',
            }
        ],
        columnLines: true,
        frame: true,
        title: 'Configure Pie Graphs and Filters',
        listeners: {
            cellclick: function(view, td, cellIndex, record, tr, rowIndex, e, eOpts){
                if(cellIndex == 3){
                    if(record.get('filter') === true){
                        if(record.get('operator') == 'matches'){
                            record.set('operator', '<');
                        } 
                        else if(record.get('operator') == '<'){
                            record.set('operator', '>');
                        }
                        else{
                            record.set('operator', 'matches');
                        }
                    }
                }
            }
        }
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
        style: { marginLeft: '15px' },
        handler: function() {
            loadMetadata();
        }
    });

    var form = Ext.create('Ext.form.field.Text', ({
        id: 'sra_list',
        bodyPadding: 10,
        width: 370,
        labelWidth: 160,
        fieldLabel: 'Sequence Read Archive IDs',
    }));
    
    var toppanel =  Ext.create('Ext.form.Panel', ({
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
            text: 'Load LGTView',
        }]
    }));

    var vp = new Ext.Viewport({
        layout: 'border',
        autoScroll: true,
        defaults: {split: true},
        items: [toppanel,middlepanel,lastpanel]
    });

    vp.doLayout();

    function loadMetadata(){
        var val = Ext.ComponentQuery.query('#sra_list')[0].getValue();
        var conf = {
            'file': val
        }
        if(val){
            Ext.Ajax.request({
                url: EXTRACT_METADATA_URL,
                // This could take some time if there are numerous LGTSeek outputs
                timeout: 600000, 
                params: conf
            });
            table.load();
        }
    }
});
