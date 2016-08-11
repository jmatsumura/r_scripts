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
my $base_dir = "./sra_list2.txt";
my $metadata_file = "/sra_metadata.csv";
my $lgt_hits_file = "/lgt_by_clone.txt";
my $blast_results_file = "/blastn.out";
my $blast_list = "./blast_list.txt";
my $uniq_sra = 0; # check to see if multiple SRA results are present
my @overall_metadata; # compile a list of metadata fields that have values tied to them
my @individual_metadata; # array of arrays for each set of headers present

open(my $sra_list_file, "<$base_dir" || die "Can't open file $base_dir");
open(my $blast_list_file, ">$blast_list" || die "Can't open file $blast_list");

# Would make sense to run this in parallel, implement this if the number of files gets
# to be quite high. 
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
			push @sra_headers, 'curation_note'; # account for TB curation note here
			$firstLine = 1;
			push @individual_metadata, \@sra_headers;
	
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
					next;
				} else {
					# Use this final dataset to populate the table for generateLGTView.js
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
			# Append curation_note field here for TB so that the pie charts can be
			# subsetted by an actual value and not 'Other' by default which does
			# not work as a filter.
			print $out "$line\t$curr_metadata\tcuration_note\n"; 

			$firstLine = 1;

		} else {

			my $curr_values = join("\t", @sra_values);
			print $out "$line\t$curr_values\tNA\n";
		}
	}

	close $l_infile;
	close $out;

	# Process the BLAST results so that TwinBLAST only houses those that match. This will be done by
	# refine_blast_data.pl
	#`./refine_blast_data.pl $blast_in $lgt_in $sra_dirs$single_blast`;

	print $blast_list_file "$sra_dirs$single_blast\n"; # file for merging
}

# Send the relevant JSON info for the filter/graph table in generateLGTView.js
#@overall_metadata;

close $sra_list_file;
close $blast_list_file;

# Once all the relevant directories have been processed, if multiple present need to consolidate to both
# a single BLAST file and a single metadata file to accommodate TwinBLAST viewer and LGTView loader.
if($uniq_sra > 1){

	my @uniform_metadata;

	# Building a final metadata file is not straightforward. Need to build a metadata file that
	# contains all the shared AND distinct fields between different sets of data. In addition to 
	# this restraint, the order of the metadata fields also needs to be equivalent and the order
	# maintained across the values associated with the data. The end result must be a uniform
	# header shared by all the different outputs.

	# Iterate over 2D array where each index of outer array attaches to an array of metadata fields
	foreach my $refs (@individual_metadata){
		foreach my $md_array_vals (@$refs) {
			if($md_array_vals ~~ @uniform_metadata) {
				next;
			} else {
				push @uniform_metadata, $md_array_vals;
			}
		}
	}

	# At this point, all unique metadata fields are present and they need to be used to build a 
	# final metadata file that accommodates each individual metadata file into a uniform final one. 


	# Use merge_blast_or_bam_lists.pl to merge the BLAST files
	#`./merge_blast_or_bam_lists.pl $blast_list blast $final_blast`
}
