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
