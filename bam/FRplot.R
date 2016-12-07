# This script will generate a Fragment Recruitment (FR) plot given a BAM file
# as input. BAM files are a compressed version of SAM files. This conversion can
# can be accomplished using "samtools." Popular aligners such as bowtie or 
# FR-hit are both capable of outputting a SAM file. 
#
# This script will accept two arguments along with calling it. The first 
# argument should be a path to a BAM file. ***NOTE*** the BAM file must have
# the "MD" field present in order to calculate the percent identity for each
# match. The second argument is the name/accession of the reference genome for
# labeling the plot appropriately.
#
# Author: James Matsumura

# Accept command line parameters
args<-commandArgs(TRUE)

# Use libraries to help with processing BAM data
library("rbamtools")
library("Rsamtools")

bamf=args[1]

bamfile=BamFile(bamf)

# Establish that the CIGAR and POSition data will be extracted
cig.pos <- c("cigar", "pos")

# Also extract the MD tag/field
param <- ScanBamParam(what=cig.pos, tag="MD")

# Create the BAM object and also read in the header data.
bam.data <- scanBam(bamfile, param=param)[[1]]
header.info <- scanBamHeader(bamfile)

# Remove all instances of NA. Often the case with Bowtie output.
bam.data$pos <- bam.data$pos[!is.na(bam.data$pos)]
bam.data$cigar <- bam.data$cigar[!is.na(bam.data$cigar)]
bam.data$tag$MD <- bam.data$tag$MD[!is.na(bam.data$tag$MD)]

# Store a regular expression to parse the CIGAR field. 
a <- "([0-9]*)(H|I|N|D|S|P|^)?([0-9]*)$"

# Establish a vector to hold the count of relevant CIGAR numbers.
total.m <- vector(mode="integer", length=length(bam.data$cigar))

# Iterate through each CIGAR element and count the number of 
# Matches/Mis-matches.
for(j in 1:length(bam.data$cigar)){
  c <- strsplit(bam.data$cigar[j], "M")
  split.m <- sub(a, "\\3", c[[1]])
  # check and remove any blanks
  split.m <- as.numeric(unlist(split.m))
  split.m <- split.m[!is.na(split.m)]
  total.m[j] <- sum(split.m)
}

# Store a regular expression to split the MD field on. 
b <- c("A|T|G|C|\\^")

# Establish a vector to hold the number of actual matches
matchvector <- vector(mode="integer", length=length(bam.data$pos))

# For each MD element in the BAM file, total the actual number of matches.
for(h in 1:length(bam.data$tag$MD)){
  g <- strsplit(bam.data$tag$MD[h], b)
  matchvector[h] <- sum(as.numeric(g[[1]][g[[1]] != ""]))
}

# Calculate percent identity
y <- matchvector/total.m * 100

# Generate the FR-plot
plot(bam.data$pos/1000, y, main=paste("FR-plot for", args[2], sep=" "), 
     ylab="Percent Identity", xlab="Genome Position (kb)", cex=0.3, 
     col="darkred", pch=4)

# Add lines to the plot to separate the various parts of the genome by 
# accession (for example, plasmids, chromosomes, etc.). This will only
# occur if there is more than one and less than 5 components comprising 
# the genome. This will also add a label for the exact accession for where 
# the boundaries are (reading from left to right). The range set for the 
# number of components is simply to maintain legbility in case there is 
# a great number of genetic components (numerous contigs).
if(length(header.info$targets) > 1 && length(header.info$targets) < 5) {
  for(k in 1:length(header.info$targets)){
    abline(v=header.info$targets[[k]]/1000)
    mtext(text=attr(header.info$targets[k], "names"), side=3, 
          at=header.info$targets[[k]]/1000, cex=0.8)
  }
}