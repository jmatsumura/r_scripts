#!/usr/bin/perl -w

=head1 NAME

guiblast - Add a simple graphic to a raw blast report

=head1 SYNOPSIS

Adds a bio graphics image to a raw blast report and outputs HTML.

=head1 DESCRIPTION

Simple script to add a graphics image to a blast report. Also indexes alignment files
and makes for quick retrieval by query ID.

=head1 AUTHOR - David R. Riley
Revised by James Matsumura (05/2016)

e-mail: driley@som.umaryland.edu
e-mail: jmatsumura@som.umaryland.edu

=cut

use strict;
use lib '.';
use Bio::SearchIO;
use Bio::Graphics;
use Bio::SeqFeature::Generic;
use Bio::Index::Blast;
use Bio::SearchIO::Writer::TextResultWriter;
use CGI;
use Tie::File;
use File::Basename;
use Digest::MD5 qw(md5 md5_hex md5_base64);
use URI::Escape;
use JSON;
use IPC::Open3;
use POSIX qw(strftime);
use Config::IniFiles;
use File::Slurp;
use MongoDB;

my $conf = Config::IniFiles->new( -file => "$ENV{CONF}");
my $chosen_db = $ENV{CHOSEN_DB};
my $db = $conf->val($chosen_db, 'dbname');
my $host = $conf->val($chosen_db, 'hostname');
my $mongo_conn = MongoDB->connect($host);
my $mongo_db = $mongo_conn->get_database($db);
my $mongo_coll = $mongo_db->get_collection('bwa_mapping');

# Deal with the CGI inputs.
my $cgi = CGI->new;
my $file = uri_unescape($cgi->param('file'));
my $list = uri_unescape($cgi->param('list'));
my $id = uri_unescape($cgi->param('id'));
my $leftsuff = uri_unescape($cgi->param('leftsuff'));
my $rightsuff = uri_unescape($cgi->param('rightsuff'));
my $qlist = uri_unescape($cgi->param('qlist'));

my $skip_text_alignments = 0;
my $max_hits = 20;
my $max_hsps = 20;

# Root of the web site (usually htdocs or html)
my $www_root = $ENV{WEB_ROOT};

# URL to web-accessible directory where image files are written. (Basically where in www_root are the images)
my $img_url = $ENV{IMG_URL};

# Place where blast indexes should be written.
my $idx_dir = $ENV{IDX_DIR};

# Required prefix for all files
my $prefix = $ENV{PREFIX};

my $print_list = $cgi->param('printlist');
my $fname = '';
my $md5;
my $start = $cgi->param('start');
my $limit = $cgi->param('limit');
my $index;

# Deal with a single blast file here
if($file) {
    $file = "$prefix/$file";
    # Little safety precaution here.
    #$file =~ s/\.\.//g;
    $file =~ s/\/\//\//g;
    $fname = basename($file);
    $md5 = md5_hex($file);
}

# Deal with a bunch of blast files here
if($list) {
    $list = "$prefix/$list";
    # Little safety precaution here.
    #$list =~ s/\.\.//g;
    $list =~ s/\/\//\//g;
    $fname = basename($list);
    $md5 = md5_hex($list);
}

my $indexed_file = "$idx_dir/$md5.idx";
my $indexed = -e $indexed_file;
my $list_file = "$idx_dir/$md5.list";

$index = Bio::Index::Blast->new(-filename => $indexed_file,
                                       -write_flag => 1);
                                       
# If our files are good then we'll just get to it.
if($indexed && &check_prep_status($md5)) {

    if($print_list) {
       	&print_list();
    }
    else {
        &print_html();
    }
}

# If our files aren't ready then we'll hit this.
else {
    &prep_files($index);
}

sub print_list {
#    if(! -e $list_file) {
#        my $files = &get_input_list();
#        print STDERR "About to make query list\n";
#        &make_query_list($files,$list_file);
#    }
    my @querys;
	if($qlist) {
		$qlist = "$prefix/$qlist";
    	$qlist =~ s/\/\//\//g;
		@querys = read_file($qlist);
	} else {
		tie @querys, 'Tie::File', $list_file;
	}
    my $total = scalar @querys;

	# Need to readjust amount of output if the amount present is less than
	# the limit so that repeat values aren't appended at the end. 
	if ($total < $limit) {
		$limit = $total-1; # account for 0 index
	}

	my $counter = 0;

    print "Content-type: text/plain\n\n";
    print "{total: $total,\nroot: [\n";
    map {
        my @f;
		if($qlist){
			chomp $querys[$counter];
			$f[0] = $querys[$counter];
			
			if($counter < $total-1) { # account for 0 index
				$counter++;
			}
		} else {
			@f = split(/\t/, $_);
		}

        if($f[0]) {

			# Pull annotation note from MongoDB
			my $cur_res = $mongo_coll->find( { 'read' => "$f[0]" } );
                        my @arr = $cur_res->next; # grab doc from cursor
                        my $annot_note = $arr[0]->{'curation_note'};

			if(not defined $annot_note){
				$annot_note='';
			}

   	        print to_json({'name' => $f[0],
   	                       'annot' => $annot_note
   	                      }).",\n";
   	    }
   	    else { last; }
	} @querys[$start..$start+$limit];
   	print "]}";
   	exit;    
}


sub print_html {

my $fh = $index->get_stream($id);
my $format = 'blast';
my $searchio = Bio::SearchIO->new(-noclose => 1,
                                  -format  => $format,
                                  -report_format => 0,
                                  -fh      => $fh); 

my $result = $searchio->next_result() or die "No Result.\n";

my $panel = Bio::Graphics::Panel->new(
        -length  => $result->query_length,
         -width   => 600,
         -pad_left   => 10,
         -pad_right  => 10,
      );

my $full_length = Bio::SeqFeature::Generic->new(
         -start   => 1,
         -end           => $result->query_length,
         -display_name  => $result->query_name,
      );

$panel->add_track($full_length,
         -glyph   => 'arrow',
         -tick    => 2,
         -fgcolor => 'black',
         -double  => 1,
         -label   => 1,
      );

my $track = $panel->add_track(
         -glyph   => 'graded_segments',
         -label   => 1,
         -connector  => 'dashed',
         -bgcolor => 'blue',
         -font2color => 'red',
         -sort_order => 'high_score',
         -bump => 1,
         -description => sub {
            my $feature = shift;
            return unless $feature->has_tag('description');
            my ($description) = $feature->each_tag_value('description');
            my $score = $feature->score;
            #use Data::Dumper;
            #print STDERR Dumper $feature;
           #my $eval = $feature->evalue;
            #my $pid = $feature->percent_identity;
            "$description";
            },
      );
my $i = 0;
while (my $hit = $result->next_hit) {
#    last if $i >= $max_hits;
 ##next unless $hit->significance < 1E-20;
   my $feature = Bio::SeqFeature::Generic->new(
         -display_name  => $hit->name,
         -score         => $hit->raw_score,
         -tag           => {
                  description => $hit->description.", score=".$hit->raw_score."|".($hit->frac_identical*100)."% identical"
                  },
         );
   my $best_eval = $hit->significance; 
   #print STDERR "$hit->name\n";
#   my $hsp = $hit->next_hsp;
   while(my $hsp = $hit->next_hsp ) {
#   my $feature = Bio::SeqFeature::Generic->new(
#         -display_name  => $hit->name,
#         -score         => $hsp->bits,
#         -start         => $hsp->start,
#         -end           => $hsp->end, 
#         -tag           => {
#                  description => $hit->description.", score=".$hsp->bits."|".($hsp->frac_identical*100)."% identical"
#                  },
#         );
      if($hsp->significance <= $best_eval) {
      $feature->add_sub_SeqFeature($hsp,'EXPAND');
      }
#   $track->add_feature($feature);
   }
   $track->add_feature($feature);
   $i++;
}

my ($url,$map,$mapname);

   if($skip_text_alignments) {
       ($url,$map,$mapname) = $panel->image_and_map(-root => $www_root,
                         -url => $img_url,
                         -link => 'http://ncbi.nlm.nih.gov/nuccore?term=$name',
                         -mapname => "$id");

    }
    else {
        ($url,$map,$mapname) = $panel->image_and_map(-root => $www_root,
                         -url => $img_url,
                         -link => '#$name',
#                         -onclick => "Ext.get('$name').scrollIntoView()",
                         -mapname => "$id");
    }
my $stream = $index->get_stream($id);
#open WH, *STDOUT;
#open (WH, ">", "$file.html");
print "Content-type: text/html\n\n";
#print  "<html>\n<body>\n<pre>";
print "<pre>";

my $last=0;
my $parsed_query = 0;
while (<$stream>) {
   if (/^.?BLAST/ || (/^Query=/ && $parsed_query)) {
      $last++;
      if ($last >1) {last};
   }
   my $line = $_;
   if($skip_text_alignments && $line =~ /^>/) {
        last;
   }
   if($line =~ /^Query/) {
       $parsed_query = 1;
   }
   if ($line =~ m/^\>(\S+)/) {
     print  "<a target='_blank' href='http://ncbi.nlm.nih.gov/nuccore?term=$1' name=$1> $line</a>\n";
   }
   elsif($line =~ /^\s+Score\s+E/) {
      print  "</pre>\n";
      print  "$map\n";
      print   qq(<img src="$url" usemap="#$mapname">),"\n";
      print  "<pre>\n";
      print $line;
   } 
   else {print $line;}
} 
print "</pre>";
#print  "</pre>\n</body>\n</html>\n";

close $stream || die "error\n";
#close WH || die "error\n";
}

sub make_query_list {
    my $files = shift;
    my $file = shift;
    open OUT, ">$file" or die "Unable to open list file $file for writing\n";    
    foreach my $f (@$files) {
        open(GREP, "grep Query= $f |"); 
        while(my $line = <GREP>) {
        chomp $line;
        $line =~ s/Query= //;
        $line =~ s/$leftsuff$//;
        $line =~ s/$rightsuff$//;;
        print OUT "$line\n";
        }
    }
    close OUT;
    `sort -u $file > $file\_sorted`;
    `mv $file\_sorted $file`;

    return $file;
}

sub get_input_list {
    my $files;
    if($list) {
        open IN, "<$list" or die;
        while(<IN>) {
            chomp;
            s/\.\.//g;
            push(@$files, $_);
        }
    }
    else {
        #$files =~ s/\.\.//g;
        $files = [$file];
    }
    return $files;
}

sub fork_proc {
    my $proc = shift;
    my $file = shift;
    my $pid;
    if($pid = fork()) {
        #print "$pid and $$\n";
    }
    elsif(defined($pid)) {
    
        # If there is a pid file already double check that 
        # someone isn't already working on this.
        if(-e $file) {
            print STDERR "Checking on $file I am $$\n";
            &check_prep_status($md5);
        }
        `echo $$ > $file`;
        print STDERR "About to execute proc from $$\n";
        &$proc();
        if(-e $file) {
            `rm $file`;
        }
        else {
            print STDERR "Had an issue, couldn't delete the pid file $pid\n";
        }
        print STDERR "$$ is exiting, all done\n";
        &print_message();
        exit;
    }
    else {
        print STDERR "Unable to fork\n";
    }
    
    return $pid;
}


sub check_proc {
    my $file = shift;
    
    my $ret = 0;
    if( -e $file) {
        my $pid = `cat $file`;

        if(kill 0, $pid) {
            $ret = $pid;
        }
        else {
            $ret = 'died';
        }
    }

    return $ret;
}

sub prep_files {
    my $index = shift;
    my $sub = sub {
        print STDERR "Creating .idx\n";
        
        # Make sure nobody is doing this already
        my $p = `cat $idx_dir/$md5.pid`;
        chomp $p;
        print STDERR "Checking $p I am  $$\n";
        if($$ != $p) {
            &check_prep_status($md5);
            if(! -e "$idx_dir/$md5.pid") {
            print "Content-type: text/plain\n\n";
            my $time = strftime "%a %b %e %H:%M:%S %Y", gmtime;
                print to_json(

                {message => "The BLAST data for this page is being prepped. The process is still going (last checked at $time).<br/>This box will update automatically when the process is complete.<br/><br/>Feel free to navigate away and come back later to check on it.",
                success => 1});
                exit;
            }
            print STDERR "pid file was there for $p. I am $$\n";
        }
        # Get all the blast reports
        my $files = &get_input_list();
        
        # Make a blast index.
        $index->make_index(@$files);
        
        # Make a query list file.
        &make_query_list($files,$list_file);
    };

    &fork_proc($sub,"$idx_dir/$md5.pid");
#    &print_message();
    exit;
}

# Check the prep status. Currently thing subroutine will exit with json formatted
# messages if the process is still running.
sub check_prep_status {
    my $md5 = shift;
    my $pid = &check_proc("$idx_dir/$md5.pid");
    chomp $pid;
    print STDERR "Got $pid I am $$\n"; 
    # Return immediately if the prep is done. No need to waste time.
    return 1 if(! $pid);
    print "Content-type: text/plain\n\n";
    my $time = strftime "%a %b %e %H:%M:%S %Y", gmtime;
    # Return an error message if the prep pid died before completing
    if($pid eq 'died') {
        print to_json(
            {message => "The prep process appears to have failed as of $time.",
            success => 0});
        exit;
    }
    # Return a message saying that the prep is still going. Return a datestamp so the user knows things
    # are still happening.
    elsif($pid !=0) {
        print STDERR "$$ is exiting\n";
        print to_json(
            {message => "The BLAST data for this page is being prepped. The process is still going (last checked at $time).<br/>This box will update automatically when the process is complete.<br/><br/>Feel free to navigate away and come back later to check on it.",
            success => 1});    
    exit;
    }
}

sub print_message {
    print "Content-type: text/plain\n\n";
    my $time = strftime "%a %b %e %H:%M:%S %Y", gmtime;
    print to_json(
        {message => "The BLAST data for this page is being prepped. The process is still going (last checked at $time).<br/>This box will update automatically when the process is complete.<br/><br/>Feel free to navigate away and come back later to check on it.",
         success => 1});  

}


