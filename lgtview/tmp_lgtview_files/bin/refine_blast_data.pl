#!/usr/bin/perl -w

=head1 NAME

refine_blast_data.pl

=head1 SYNOPSIS

Script to refine raw BLAST results to only those hits that are present in another file

=head1 DESCRIPTION

This script takes three arguments:

--blast_file  = /path/to/blast/file
--id_list = /path/to/id/list
--out_file = /path/to/output/file

Thus, to use this script you would enter:

./conceal_blast_data.pl --blast_file=blast.results --id_list=id_list.txt --out_file=my_concealed_blast.results

Note that the id_list.txt file just needs any trace of the read present and does not
require a specific format. Thus, be wary of this as the BLAST file will include any results
that match ANY trace of a particular read in the id_list.txt file.

=head1 AUTHOR - James Matsumura

e-mail: jmatsumura@som.umaryland.edu

=cut

use strict;
use warnings;

my $blast_file = $ARGV[0];
my $id_list = $ARGV[1];
my $out_file = $ARGV[2];

if ( @ARGV != 3) {
	print "Incorrect number of arguments. Please ensure the correct usage described at the ".
			"top of this script";
	exit(1);
}

open(my $out, ">$out_file") or die "Cannot open $out_file for writing";
open(my $fh, $blast_file) or die "Can't open $blast_file!";

my $blast_entry; # start fresh at every entry, only include those that are relevant
my $read_id;
my $found_entry = 0;
my $valid_pair = 0; # know that read pairs follow one another, so print the second one fast
my $entry_count = 0; # aids in delimiting different entries
my $footer = 0;

while (my $line = <$fh>) {

	if($found_entry == 1){

		if($line =~ /^BLAST.*/) {
			$found_entry = 0;
			$blast_entry .= "\n\n";
            
            # This is the point where if this result is tied to one of the results from the
            # metadata file it must be included. The metadata file should already have subsetted
            # the data to be that belonging only to pairs so no need to do a check for that here. 
			# Need to iterate over this file each time.
			open(my $fh2, $id_list) or die "Can't open $id_list!"; 
			while (my $line2 = <$fh2>) {
				if($line2 =~ /$read_id/){
					print $out $blast_entry;
					$valid_pair = 1;
					last;
				}
			}
			close $fh2;

			# The BLAST result has been processed, OK to reinitialize all.
			$read_id = '';
			$blast_entry = '';
			$blast_entry .= $line;
   
		} elsif($line =~ /^Query=.*/) {
			$blast_entry .= $line;
			$line =~ /^Query=\s(.*)\/(1|2)$/;
			$read_id = quotemeta "$1";

		} else { # inbetween sections, append to entry regardless
			$blast_entry .= $line;
		}

	} elsif($valid_pair == 1) {
	
		if($line =~ /^BLAST.*/) {

			$blast_entry .= $line;
			$entry_count++;

			if($entry_count == 2) { # found the first mate in a pair again
				print $out $blast_entry;
				$entry_count = 0;
				$valid_pair = 0;
				$found_entry = 1;
			}

		} elsif($line =~ /\s\sDatabase:.*/) { # In case this is at the end of file
			print $out $blast_entry;
			$valid_pair = 0;

		} else { # lines inbetween entries
			$blast_entry .= $line;
		}

	# Tag on the end total BLAST search report at the end of the file so that further
	# modules can parse the file correctly. Note that this data will be incorrect if any
	# of the initial results are removed. These results are not used in TwinBLAST though.
	} elsif($line =~ /\s\sDatabase:.*/) {
		$footer = 1;
		print $out $line;

	} elsif($footer == 1) {
		print $out $line;

	} else {

		if($line =~ /^BLAST.*/) {
    	    $found_entry = 1;
			$blast_entry .= $line;
		} else { # already seen the BLAST header and still in the main body
			$found_entry = 1;
		}
	}
}

close $fh;
close $out;
