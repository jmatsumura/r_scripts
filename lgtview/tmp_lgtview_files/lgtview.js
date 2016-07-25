Ext.Loader.setPath('Ext.ux', 'ux');
Ext.Loader.setConfig({enabled: true});

Ext.onReady(function(){
     var conf = {
        db: 'lgtview_example',
        host: '172.18.0.1:27017',
		site: 'https://localhost:443/twinblast.html'
		site: 'http://localhost:8080/twinblast.html'
    };
    var allStores = [];
    var portlets = {
        0 : [],
        1: []};

    var get_metadata = 0;
    Ext.regModel('gene',{
    });

    var offset = 0;

// START CHART SECTION
    addWindow({'name': 'euk_genus',
               'title': 'Euk Genus',
               'modname': 'euk_genus'
              });

    addWindow({'name': 'euk_ref',
               'title': 'Eukaryote Mappings',
               'modname': 'euk_ref'});

    addWindow({'name': 'bac_genus',
               'title': 'Bac Genus',
               'modname': 'bac_genus'});
// END CHART SECTION

    Ext.regModel('filters',{
        fields: [
            {name: 'key',type: 'string'},
            {name: 'value', type: 'string'},
            {name: 'op', type: 'string'}
        ]
    });
    var filterstore = new Ext.data.Store({
        model: 'filters',
        proxy: {
            type: 'memory',
            reader: {
                type: 'json',
                root: 'loads'
            }
        }
    });    
    var cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
        clicksToEdit: 1
    });
    var filtergrid = new Ext.grid.Panel({
        store: filterstore,
        forcefit: true,
        anchor: '100%, 100%',
        flex: 1,
        selModel: {
            selType: 'cellmodel'
        },
        plugins: [cellEditing],
        columns: [
            {text: 'Key', dataIndex: 'key', type: 'string',width: 80},
            {header: 'Op',
            dataIndex: 'op',
            width: 60,
            field: {
                xtype: 'combobox',
                typeAhead: true,
                triggerAction: 'all',
                selectOnTab: true,
                store: [
                    ['=','eq'],
                    ['!=','ne']
                ],
                lazyRender: true,
                listClass: 'x-combo-list-small'
            }},
            {text: 'value', dataIndex: 'value', type: 'string', width:80, editor: {xtype: 'textfield'}},

            {xtype: 'actioncolumn',
                width: 20,
                items: [{
                    icon   : 'delete.gif',  // Use a URL in the icon config
                    tooltip: 'Remove filter',
                    handler: function(grid, rowIndex, colIndex) {
                        var rec = filterstore.getAt(rowIndex);
                        filterstore.remove(rec);
                        loadData();
                    }
                }]
            }
        ]
    });

// START FILTER SECTION 1
    var min_euk_len = new Ext.form.field.Text({
        fieldLabel: 'min euk length',
        value: 15,
        name: 'min_euk_len'
    });
    var min_bac_len = new Ext.form.field.Text({
        fieldLabel: 'min bac length',
        value: 15,
        name: 'min_bac_len'
    });
    var chosen_euk_genus = new Ext.form.field.Text({
        fieldLabel: 'eukaryote genus',
        name: 'chosen_euk_genus'
    });
    var chosen_bac_genus = new Ext.form.field.Text({
        fieldLabel: 'bacteria genus',
        name: 'chosen_bac_genus'
    });
    var filterform = new Ext.form.Panel({
        width: '100%',
        frame: true,
        items: [min_euk_len,min_bac_len,chosen_euk_genus,chosen_bac_genus]
    });
// END FILTER SECTION 1

    Ext.regModel('reads',{
    });

    var readgrid;
    var configured = false;
    var readstore = new Ext.data.Store({
        model: 'reads',
        pageSize: 100,
        proxy: {
            type: 'ajax',
			timeout: 5000000,
            url: '/cgi-bin/view.cgi',
            extraParams: {
                'db': conf.db,
                'host': conf.host
            },
            reader: {
                type: 'json',
                root: 'retval'
            }
        },
        listeners: {
            metachange : function(store,meta) {
                if(!configured && meta != undefined) {
                    Ext.each(meta.columns, function(col) {
                        if(col.dataIndex =='read') {
                            col.renderer = function(value,p,record) {
                                return '<a target=_blank href=' + conf.site + '#?id='+
                                    value+
                                    '&file=example_blastn.out>'+
                                    value+
                                    '</a>';
                            }
                        }
                    });
                    readgrid.reconfigure(store,meta.columns);
                    configured = true;
                }
            }
        }
    });
    
    readgrid = new Ext.grid.Panel({
        store: readstore,
        title: 'Reads',
        region: 'south',
        forcefit: true,
        height: 300,
        split: true,
        columns: [],
        // paging bar on the bottom
        bbar: Ext.create('Ext.PagingToolbar', {
            store: readstore,
            displayInfo: true,
            displayMsg: 'Displaying reads {0} - {1} of {2}',
            emptyMsg: "No reads to display"
        }),
    });
    var bacwin = new Ext.Panel({
        title: 'Bacterial Mappings',
        layout: 'fit',
        split: true,
        region: 'east',
        width: 500,
        autoScroll: true,
        loader: {
            loadMask: false
        },
        items: [{
            xtype : 'component',
            id    : 'bac-iframe',
            autoEl : {
                tag : "iframe",
            }
        }]
    });

	var titlebar = new Ext.Panel({
		height: 54,
        region: 'north',
        forcefit: true,
        layout: 'hbox',
        items: [
        {width: 260,
        xtype: 'container',
        html: '<img height=50px src=lgtview_logo_50px_trans.png>'},
        {width: 800,
        xtype: 'container',
            padding: '10 0 0 10',
		html: '<i>The reads below are putative Lateral Gene Transfer reads. They are paired-end reads where one mate maps to a donor genome and the other mate maps to a host genome. Clicking on the pie charts will filter the reads in the display. Selecting/deselecting elements from the \'filters\' section will also change the reads in the display. Clicking on a read name in the \'read\' column will open a page with BLAST results for that read.</i>'},
        {flex: 1,xtype: 'container'}
        ]
	});

    var vp = new Ext.Viewport({
        items: [titlebar,
            {xtype: 'portalpanel',
             id: 'portalpanel',
             region: 'center',
             title: 'Graphs',
             items: [{
                 items: portlets[0]
             },{
                 items: portlets[1]
             }]
            },readgrid,
            bacwin,
            {layout: 'fit',
            region: 'west',
            title: 'Filters',
            buttons: [{text: 'reload',handler: function() { loadData()}},
					 {text: 'tab-delimited', handler: function() { getText('dl')}}],
            split: true,
            items: [{layout: 'anchor',
                     items: [
                         filterform,
                         filtergrid]
                    }],
             width: 300}],
        layout: 'border',

    });

    allStores.push(readstore);
    var allfilters = {};
    loadData();

	function getFilters() {
        allfilters = {};
        filterstore.each(function(rec) {
            var val = rec.data.value;
            if(rec.data.type =='numeric') {
                val = rec.data.value*1;
            }
            if(rec.data.op == '=') {
                allfilters[rec.data.key] = val;
            }
            else if(rec.data.op == '!=') {
                allfilters[rec.data.key] = {'$ne': val};
            }
        });

// START FILTER SECTION 2
        if(min_euk_len.getValue() != '') {
            allfilters['euk_len'] = {'$gt': min_euk_len.getValue()*1};
        }
        if(min_bac_len.getValue() != '') {
            allfilters['bac_len'] = {'$gt': min_bac_len.getValue()*1};
        }
        if(chosen_euk_genus.getValue() != '') {
            allfilters['euk_genus'] = {'$regex': chosen_euk_genus.getValue()};
        }
        if(chosen_bac_genus.getValue() != '') {
            allfilters['bac_genus'] = {'$regex': chosen_bac_genus.getValue()};
        }
// END FILTER SECTION 2

        return allfilters;
    }
	
	function getText(out_type) {
        var filters = getFilters();
		var params;

        // Download text here
		if(out_type == 'dl') {
       		params = {
        	    cond: Ext.encode(filters),
				file_format: out_type,
        	    format: 'text'
        	}
		}

		else if(out_type == 'local') {
			var vals = hm_form.getValues();
       		params = {
        	    cond: Ext.encode(filters),
				file_format: out_type,
        	    format: 'text',
				infile: vals.inp_infile,
				tax_rank: vals.inp_tax_rank,
				chosen_metadata: vals.inp_chosen_metadata,
				abundance_type: vals.inp_abundance_type
        	}
		}

        Ext.apply(params,conf);
        var request = Ext.urlEncode(params);
        if (!Ext.fly('frmDummy')) {
            var frm = document.createElement('form');
            frm.id = 'frmDummy';
            frm.name = frm.id;
            frm.className = 'x-hidden';
            document.body.appendChild(frm);
        }
        Ext.Ajax.request({
            method: 'POST',
            timeout: 5000000,
            isUpload: true,
            form: Ext.fly('frmDummy'),
            url: '/cgi-bin/view.cgi',
            params: params,
            success: function(response){
                var res = Ext.decode(response.responseText);
                Ext.getDom('bac-iframe').src = res.file;
            }
        });
    }

	// Need to add a 'plot_type' option here to differentiate between
	// the various panels. 
    function loadData(caller,cond,plot_type) {
        appendFilter(cond);
        allfilters = {};
        filterstore.each(function(rec) {
            if(rec.data.op == '=') {
                allfilters[rec.data.key] = rec.data.value;
            }
            else if(rec.data.op == '!=') {
                allfilters[rec.data.key] = {'$ne': rec.data.value};
            }
        });

// START FILTER SECTION 2
        if(min_euk_len.getValue() != '') {
            allfilters['euk_len'] = {'$gt': min_euk_len.getValue()*1};
        }
        if(min_bac_len.getValue() != '') {
            allfilters['bac_len'] = {'$gt': min_bac_len.getValue()*1};
        }
        if(chosen_euk_genus.getValue() != '') {
            allfilters['euk_genus'] = {'$regex': chosen_euk_genus.getValue()};
        }
        if(chosen_bac_genus.getValue() != '') {
            allfilters['bac_genus'] = {'$regex': chosen_bac_genus.getValue()};
        }
// END FILTER SECTION 2

		if(typeof plot_type === undefined){
        	// Reload the Krona Plot here
        	var kronaparams = {
        	    cond: Ext.encode(allfilters),
        	    format: 'krona',
        	    condfield: 'bac_blast_lca'
        	}
        	Ext.apply(kronaparams,conf);
        	Ext.Ajax.request({
        	    url: '/cgi-bin/view.cgi',
        	    params: kronaparams,
        	    success: function(response){
        	        var res = Ext.decode(response.responseText);
        	        Ext.getDom('bac-iframe').src = res.file;
        	    }
        	});
        }

		else if(plot_type == 'heatmap'){
			getText('local');
		}

        Ext.each(allStores, function(store) {
        
                Ext.apply(store.getProxy().extraParams,
                    {cond: Ext.encode(allfilters),
                });
                store.load();
        });
    }
    
    function appendFilter(filter) { 
        for(i in filter) if (filter.hasOwnProperty(i)) {
            if(filterstore.findRecord('key',i)) {
                var rec = filterstore.findRecord('key',i);
                rec.set('value',filter[i]);
                rec.set('op', '=');
            }
            else {
                filterstore.add({
                    'key': i,
                    'op': '=',
                    'value': filter[i]
                });
            }
        }
    }

    function addWindow(params) {

        Ext.regModel(params.modname,{
        fields: [
            {mapping: '_id',name: params.name,type: 'string'},
            {name: 'count', type: 'int'}
        ]
        });
        var newstore = new Ext.data.Store({
            model: params.modname,
            autoLoad: false,
            proxy: {
                type: 'ajax',
                url: '/cgi-bin/view.cgi',
                extraParams: {
                    'criteria': params.name,
                    'db': conf.db,
                    'host': conf.host,
                },
                reader: {
                    type: 'json',
                    root: 'retval'
                }
            }
        });
        var newchart = new Ext.chart.Chart({
            animate: true,
            store: newstore,
            shadow: false,
            legend: {
                position: 'right'
            },
            theme: 'Base:gradients',
            series: [{
                type: 'pie',
                field: 'count',
                listeners: {

                    'itemmouseup': function(item) {
                        var newparams = [];
                        newparams[params.name] = item.storeItem.data[params.name];
                        loadData(newstore,newparams);
                    }
                },
                tips: {
                    width: 250,
                    renderer: function(storeItem, item) {
                        var title = 'Unknown';
                        if(storeItem.get(params.name)) {
                            title = storeItem.get(params.name);
                        }
                        this.setTitle(title+'<br/>'+storeItem.get('count')+' reads');
                    }
                },
                highlight: {
                    segment: {
                        margin:20
                    }
                },
                label: {
                    field: params.name,
                    display: 'rotate',
                    contrast: true
                }
            }]
        });
        allStores.push(newstore);
        if(portlets[0].length <= portlets[1].length) {
            portlets[0].push({title: '' + params.name,
                              height: 200,
                              items: newchart});
        }
        else {
            portlets[1].push({title: '' + params.name,
                              height: 200,
                              items: newchart});
        }
        
        offset = offset + 50;
    }
});