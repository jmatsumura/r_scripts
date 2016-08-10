#!/usr/bin/perl -w

=head1 NAME

build_metadata_table.cgi

=head1 SYNOPSIS

Script to build a metadata table for the intermediary site of LGTView.

=head1 DESCRIPTION

This script takes a single argument: 

- A file that contains the directory paths which house the relevant output files 
from LGTSeek. For each directory provided, this script will then access the 
respective metadata file, the BLASTN raw results file, and the respective LGT
out results file. If multiple directories are present then these BLAST results
must be merged as well as providing the metadata fields which actually have 
a value assigned to them for at least one group. 

The primary purpose of this script is to populate the generateLGTView.html site 
with a table that users can interact with to generate their custom instance
of LGTView. 

=head1 AUTHOR - James Matsumura

e-mail: jmatsumura@som.umaryland.edu

=cut

use strict;
use warnings;
#use CGI;
#use JSON;

# Need to process multiple outputs of LGTSeek as LGTView is truly useful when comparing
# numerous different sets of metadata against one another. 
my $base_dir = "./sra_list.txt";
my $metadata_file = "/sra_metadata.csv";
my $lgt_hits_file = "/lgt_by_clone.txt";
my $blast_results_file = "/blastn.out";
my $uniq_sra = 0; # check to see if multiple SRA results are present
my @overall_metadata; # compile a list of metadata fields that have values tied to them

open(my $sra_list_file, "<$base_dir" || die "Can't open file $base_dir");

while (my $sra_dirs = <$sra_list_file>) { # process each SRA LGTSeek output result

	chomp $sra_dirs;
	my $in = $sra_dirs . $metadata_file;
	open(my $infile, "<$in" || die "Can't open file $in");
	$uniq_sra++;

	my $firstLine = 0;
	my @sra_headers; # metadata fields
	my @sra_values;

	while (my $line = <$infile>) {

		chomp $line;

		if($firstLine == 0) {
			@sra_headers = split(/\,/, $line); # banking on SRA using commas for separation only 
			$firstLine = 1;
	
		} else {
			@sra_values = split(/\,/, $line); 
		}
	}

	close $infile;

	my $idx = 0;

	# Only concerned with those metadata fields that have a value and aren't a hash value.
	foreach my $x (@sra_values){

		if($x ne ''){ 

			if($sra_headers[$idx] ne 'ReadHash' && $sra_headers[$idx] ne 'RunHash'){

				if($sra_headers[$idx] ~~ @overall_metadata) {
					continue;
				} else {
					# Build a final set of metadata from all metadata present
					push @overall_metadata, $sra_headers[$idx];
				}
			}
		}

		$idx++;
	}

=head
	# Process the BLAST results so that TwinBLAST only houses those that match. This will be done by
	# refine_blast_data.pl
	$sra_dirs =~ /^.*\/(.*)$/; # grab the SRA ID
	$sra_id = $1;
	my $tb_outfile = "./" . $sra_id . "_blast.out";
	`./refine_blast_data.pl --blast_file=$blast_file --id_list=$lgt_hits --out_file=$tb_outfile`;
=cut
}

# Once all the relevant directories have been processed, if multiple present consolidate to 
# a single BLAST file to accommodate TwinBLAST. This functionality will be accomplished by 
# merge_blast_or_bam_lists.pl 
