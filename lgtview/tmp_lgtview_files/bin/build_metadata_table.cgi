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

# Output files that will be expected 
my $single_metadata = "/single_metadata.out"; # just one run output
my $single_blast = "/single_blast.out";
my $final_metadata = "./final_metadata.out"; # combined run outputs
my $final_blast = "./final_blast.out";

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

	$uniq_sra++;

	chomp $sra_dirs;
	my $meta_in = $sra_dirs . $metadata_file;
	my $lgt_in = $sra_dirs . $lgt_hits_file;
	my $blast_in = $sra_dirs . $blast_results_file;

	my @sra_headers; # metadata fields
	my @sra_values;

	my $firstLine = 0;

	open(my $m_infile, "<$meta_in" || die "Can't open file $meta_in");

	while (my $line = <$m_infile>) {
		chomp $line;

		if($firstLine == 0) {
			@sra_headers = split(/\,/, $line); # banking on SRA using commas for separation only 
			$firstLine = 1;
	
		} else {
			@sra_values = split(/\,/, $line); 
		}
	}

	close $m_infile;

	my $idx = 0;

	# For letting a user choose which metadata to display, only concerned with those metadata 
	# fields that have a value and aren't comprised of a hash value.
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

	# Now append all metadata from SRA to the lgt_by_clone.txt file. Add handling in this
	# section if certain fields, like the hashes or consent, are desired to be omitted. 

	$firstLine = 0;

	open(my $l_infile, "<$lgt_in" || die "Can't open file $lgt_in");
	open(my $out, ">$sra_dirs$single_metadata" || die "Can't open file $lgt_in");

	while (my $line = <$l_infile>) {
		chomp $line;

		if($firstLine == 0){

			my $curr_metadata = join("\t", @sra_headers);
			print $out "$line\t$curr_metadata\n";

			$firstLine = 1;

		} else {

			my $curr_values = join("\t", @sra_values);
			print $out "$line\t$curr_values\n";
		}
	}

	close $l_infile;
	close $out;

	# Process the BLAST results so that TwinBLAST only houses those that match. This will be done by
	# refine_blast_data.pl
	#$sra_dirs =~ /^.*\/(.*)$/; # grab the SRA ID
	#$sra_id = $1;
	`./refine_blast_data.pl $blast_in $lgt_in $sra_dirs$single_blast`;
}

# Once all the relevant directories have been processed, if multiple present consolidate to 
# a single BLAST file to accommodate TwinBLAST. This functionality will be accomplished by 
# merge_blast_or_bam_lists.pl 
