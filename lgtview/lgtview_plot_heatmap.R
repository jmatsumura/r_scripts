# This script will take in a metadata file formatted for LGTView. It finds
# whichever column is associated with the header 'bac_blast_lca:list' and
# builds a heatmap using relative abundances of those OTUs. Users will be 
# able to specify the level of taxonomy in order to generate a heatmap at
# a level which suits their particular needs. The second dimension to the 
# heatmap will also need to be specified and has to be found within that
# same metadata file. 
#
# This script is meant to be invoked from LGTView but it can be run on the
# command line like so:
#
# Rscript lgtview_plot_heatmap.R tax_# metadata_header abundance_type
# tax_# = taxonomic rank used to build the heatmap. Note that there are
# often numerous classically unranked assignments made here. Meaning, it
# doesn't follow strictly domain;kingdom;phylum;etc. Thus, the user will
# specify a number here that will, starting from the highest level found,
# will go down to as specific as they mention. So if the OTU is:
# cellular organisms;Eukaryota;Opisthokonta;Metazoa
# And the user enters 2 it will return domain-level results. 
#
# metadata_header = will map to any of the headers present within the metadata
# file. Thus, leading to the heatmap to be (chosen_metadata,OTUs) as the (x,y)
# abundance_type = either 'relative' or 'absolute' depending on whether the user
# wants relative counts or absolute counts for how many hits to that particular
# OTU.
#
# Author: James Matsumura
#
# Contact: jmatsumura@som.umaryland.edu

library("plyr")

# Accept command line arguments
args <- commandArgs(TRUE)

# Assign file path, taxonomic rank, chosen metadata, abundance type
file.path <- args[1]
taxonomic.rank <- as.numeric(args[2])
chosen.metadata <- args[3]
abundance.type <- args[4]

# Start as a dataframe until abundances are calculated. Only filling on the
# offchance that some odd characters were introduced into an OTU name like
# '#' which causes issues for R's parsing. 
data <- read.table(file=file.path, header=T, sep="\t", fill=T)

# X df is whichever metadata is specified
x.col <- as.data.frame(data[,chosen.metadata])

# Y df is, for now, going to be set as the taxonomic assignment for bac read
y.col <- as.data.frame(data[,"bac_blast_lca.list"])
ydf <- data.frame(matrix(nrow=length(y.col[,1]),ncol=1))
names(ydf)[1]<-"tax"

# First do an absolute count of each OTU present.
for(i in 1:length(y.col[,1])){
  
  taxonomy <- strsplit(as.character(y.col[i,1]),";")
  
  # First account for when the user asks for more specific than was found
  if(length(taxonomy[[1]]) < taxonomic.rank){
    tax_assignment <- "unclassified"
  } else { # now handle if it is indeed present
    tax_assignment <- taxonomy[[1]][taxonomic.rank]
  }
  
  # Sharing complete lineage will help more readily ID trends
  if(taxonomic.rank > 1){
    #final_tax_assignment <- paste(taxonomy[[1]][1:taxonomic.rank-1], tax_assignment, collapse=";", sep=";")
    mod_tax_assignment <- paste(taxonomy[[1]][1:taxonomic.rank-1], collapse=";")
    final_tax_assignment <- paste(mod_tax_assignment, tax_assignment, sep=";")
  }

  # Append to DF that will be used to calculate abundance
  ydf[i,1] <- final_tax_assignment
  #print(count(ydf, "ncol"))
  
}

# This will perform the count of each unique type of row to get an abundance
ydf_counts <- ddply(ydf, .(tax), c("nrow"))

# Going to build a hash for quick lookup when assigning values to heatmap matrix
count_hash<-new.env()

# Already in absolute abundance, if relative desired then convert
if(abundance.type == "relative"){
  
  total <- sum(ydf_counts[,2])
  for(i in 1:length(ydf_counts[,2])){
    count_hash[[as.character(ydf_counts[i,1])]]<-(ydf_counts[i,2]/total*100)
  }

# Building the hash slightly different for absolute (no % calc necessary)
} else {
  
  for(i in 1:length(ydf_counts[,2])){
    count_hash[[as.character(ydf_counts[i,1])]]<-ydf_counts[i,2]
  }
}

