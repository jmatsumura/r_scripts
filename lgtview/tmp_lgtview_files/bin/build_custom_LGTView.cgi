#!/usr/bin/perl -w

=head1 NAME

build_custom_LGTView.cgi

=head1 SYNOPSIS

Script which follows build_metadata_table.cgi and actually loads the
the new instance of LGTView. 

=head1 DESCRIPTION

This script will accept a JSON array of metadata items that were generated
by build_metadata_table.cgi and then re-configured by generateLGTView.js. 
These metadata will have been chosen for whether they are to be represented
as pie charts, filters, or neither within LGTView. 

The script happens in 3 main steps.

1) Extract the JSON metadata and build a file that can be processed by
configure_lgtview_for_metadata.pl. 

2) Rewrite lgtview.js via configure_lgtview_for_metadata.pl

3) Load MongoDB with the final metadata file built from build_metadata_table.cgi.
This will require the use of lgt_load_mongo.pl. Note that in its current state,
LGTView is built to only have 1 DB available at the moment. Until this has been
implemented, will have to remove old DB and load with a fresh instance each
time the generateLGTView.html site is accessed. 

=head1 AUTHOR - James Matsumura

e-mail: jmatsumura@som.umaryland.edu

=cut

use strict;
use warnings;
use CGI;
use JSON;

my $cgi = CGI->new;

my $dd = qq#
{
	"root" : [
		{	"name": "run",
			"filter": false,
			"pie": false,
			"id": "run",
			"operator": "NA"
		},
		{	"name": "test",
			"filter": false,
			"pie": true,
			"id": "test",
			"operator": "NA"
		},
		{	"name": "123",
			"filter": true,
			"pie": false,
			"id": "123",
			"operator": ">"
		}
	]
}
#;

my $data = from_json( $dd );

my $pchart_line = ''; # line 1 needed for configure_lgtview_for_metadata.pl
my $filter_line = ''; # line 2

my @md = @{ $data->{'root'} }; # deref and copy to new array

open(my $outfile, ">./config_file.tsv" || die "Can't open file ./config_file.tsv");

foreach my $m ( @md ) { # iterate over array of hashref

	my $name = $m->{'name'};
	my $filter = $m->{'filter'};
	my $pie = $m->{'pie'};
	#my $id = $m->{'id'}; ID not needed for this step, only for JS
	my $operator = $m->{'operator'};

	if($filter == 0 && $pie == 0){ # this data only needs to be loaded to MongoDB
		next;

	} elsif($pie == 1) { # append to line 1 to configure pie charts

		if($pchart_line ne '') { # separate if value already present
			$pchart_line .= "\t";
		}

		# Could get fancy here eventually and use regex to try reformat each 
		# metadata name to something more proper. e.g....
		# spots_with_mates --> Spots With Mates
		# LibrarySource --> Library Source
		$pchart_line .= "$name|$name";

	} elsif($filter == 1) { # append to line 2 to configure filters

		if($filter_line ne '') {
			$filter_line .= "\t";
		}

		$filter_line .= "$name|";

		if($operator eq 'matches'){
			$filter_line .= "l";

		} elsif($operator eq '<') {
			$filter_line .= "n|<";

		} elsif($operator eq '>') {
			$filter_line .= "n|>";
		}
	}
}

close $outfile;

print "$pchart_line\n$filter_line";
