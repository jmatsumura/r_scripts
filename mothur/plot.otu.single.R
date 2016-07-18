# This script will generate a bar plot given OTU data from a single sample. 
# The user decides at what taxonomy rank they would like to view the data at
# and whether or not they would like to include instances of 'unclassified' 
# in their data. 
#
# This script requires three arguments when it is run. The first argument is 
# the level of taxonomic classification you want to plot your data at, e.g. 
# 1=domain, 2=phylum, 3=class, 4=order, 5=family, and 6=genus. The second 
# argument is either "Y" or "N" for whether you would like to include the 
# unclassified entries in your output. If you would like to get an idea of 
# how well classified your data is, please use the complementary script 
# "otu.stats.R". The third argument is the path to an OTU file produced from 
# the analysis software mothur. This is a tab-delimited file of three columns: 
# OTU, size, and taxonomy. Note that the taxonomy must span from domain through 
# genus, leaving any unknowns as 'unclassified'. 
#
# Please refer to the OTU section of this SOP from the authors of mothur for
# more details on how to generate the file: http://www.mothur.org/wiki/454_SOP
#
# Example of how to plot at the class taxonomic level with unclassified entries: 
# Rscript plot.otu.single.R 3 "Y" "/path.to.my.file"
#
# Author: James Matsumura

# Accept command line parameters
args<-commandArgs(TRUE)

# Load library to help with plotting
library("ggplot2")

# Assign args to variables
tax.level=as.numeric(args[1])
class.or.unclass=args[2]
file.path=args[3] 

# Read in the file and the convert to data frame
data <- read.table(file=file.path, header=T)
data <- as.data.frame(data)

# Extract the different taxonomic classification levels
data[,3] <- as.character(data[,3])
new.data <- as.data.frame(strsplit(data[,3], "\\(\\d+\\);", perl=T))
new.data <- matrix(unlist(new.data), ncol=6, byrow=TRUE)

# Count frequencies of classifications at the correct level
final.data <- as.data.frame(table(new.data[,tax.level]))

# Subset the data to remove the unclassified count if the option is set to omit
if(class.or.unclass=="N"){
  
  # Identify whether any unclassified entries are present
  subset.indices <- final.data$Var1=="unclassified"
  
  # Remake the dataframe by subsetting by those which are classified
  wo.class <- data.frame(Classification = factor(final.data$Var1[!subset.indices],
                                                 levels=final.data$Var1[!subset.indices]), 
                         Count = final.data$Freq[!subset.indices]
                         )
  final.data <- wo.class
}

# Reassign column names
colnames(final.data) <- c("Classification", "Count")

pdf("output.plot.otu.single.pdf", width = 9, height = 8)

# Plot using ggplot2
ggplot(data=final.data, aes(x=Classification, y=Count, fill=Classification)) +
  geom_bar(stat="identity") + guides(fill = guide_legend(title.theme = element_text(face="bold",angle=0))) +  coord_flip() + theme(legend.position="none")
