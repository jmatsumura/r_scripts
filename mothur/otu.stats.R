# This script will generate statistics on an OTU file from mothur. 
# Specifically, it will yield the total number of OTUs as well as the amount
# of unclassified (and consequently classified) sequences present at each
# taxonomic level. This script is meant to be used as a precursor to other
# tools so that the correct level of taxonomic classification can be used for
# downstream analyses. 
#
# This script requires one argument when it is run. This argument is the path 
# to an OTU file produced from the analysis software mothur. This is a tab-
# -delimited file of three columns: OTU, size, and taxonomy. Note that the
# taxonomy must span from domain through genus, leaving any unknowns as 
# 'unclassified'.
#
# Please refer to the OTU section of this SOP from the authors of mothur for
# more details on how to generate the file: http://www.mothur.org/wiki/454_SOP
#
# Example of how to get stats on an OTU file: 
# Rscript otu.stats.R "/path.to.my.file"
#
# Author: James Matsumura

# Accept command line parameters
args<-commandArgs(TRUE)

# Assign the path to the OTU file
file.path=args[1] 

# Read in the file and the convert to data frame
data <- read.table(file=file.path, header=T)
data <- as.data.frame(data)

# Count OTUs 
otu.count <- sum(as.numeric(data[,2]))

# Extract the different taxonomic classification levels
data[,3] <- as.character(data[,3])
new.data <- as.data.frame(strsplit(data[,3], "\\(\\d+\\);", perl=T))
new.data <- matrix(unlist(new.data), ncol=6, byrow=TRUE)

# Count the number of instances of 'unclassified' per taxonomic rank
unclass <- new.data=="unclassified"
unclass.dat <- as.data.frame(apply(unclass,2,as.numeric))

# Multiply by the size of the OTU and sum
unclass.list <- vector()
for(i in 1:6) 
{
  unclass.list[i] <- sum(data[,2]*unclass.dat[,i]*-1)
}

# Store the amount of classified entries
unclass.list <- unclass.list+otu.count

# Store the percentage of unclassified entries
p <- round((otu.count-unclass.list)/otu.count*100,4)

# Output the relevant values to the user
cat("Total OTU count: ", otu.count)
cat("\nClassified entry count at each taxonomic level",
    "\nDomain:\t",unclass.list[1],"\t", "(% unclassified =", p[1],
    ")\nPhylum:\t",unclass.list[2],"\t", "(% unclassified =", p[2],
    ")\nClass:\t",unclass.list[3],"\t", "(% unclassified =", p[3],
    ")\nOrder:\t",unclass.list[4],"\t", "(% unclassified =", p[4],
    ")\nFamily:\t",unclass.list[5],"\t", "(% unclassified =", p[5],
    ")\nGenus:\t",unclass.list[6],"\t", "(% unclassified =", p[6], ")\n")

