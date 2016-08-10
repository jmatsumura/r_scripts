#!/usr/bin/perl -w

=head1 NAME

build_metadata_table.cgi

=head1 SYNOPSIS

Script to build a metadata table for the intermediary site of LGTView.

=head1 DESCRIPTION

This script takes a single argument: 

- The directory path that houses the relevant output files from LGTSeek. 
This script will then access the metadata file, the BLASTN raw results file,
and the respective LGT out results file. 

The main purpose of this script is to populate the generateLGTView.html site 
with a table that users can interact with to generate their custom instance
of LGTView. 

=head1 AUTHOR - James Matsumura

e-mail: jmatsumura@som.umaryland.edu

=cut

use strict;
use warnings;
use CGI;
use JSON;

my $cgi = CGI->new;

my $lgtseek_out = $cgi->param('location');
my $blast_file = ($lgtseek_out . "/blastn.out");
my $lgt_hits = ($lgtseek_out . "/lgt_by_clone.txt");
my $sra_metadata = ($lgtseek_out . "/sra_metadata.csv");
my $sra_id;

if($lgtseek_out){
	$lgtseek_out =~ /^.*\/(.*)$/; # grab the SRA ID
	$sra_id = $1;
}

my $tb_outfile = "./" . $sra_id . "_blast.out";

# Process the BLAST results so that TwinBLAST only houses those that match.
`./refine_blast_data.pl --blast_file=$blast_file --id_list=$lgt_hits --out_file=$tb_outfile`;
