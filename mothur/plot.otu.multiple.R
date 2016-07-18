# This script will plot multiple samples given multiple different OTU files
# from mothur. This is ideally to be used for comparison of the different 
# compositions between different samples. The output will be a stacked 
# bar plot with each bar representative of a single sample. 
#
# This script requires a minimum of four arguments when it is run. The first 
# argument is the level of taxonomic classification you want to plot your data 
# at, e.g. 1=domain, 2=phylum, 3=class, 4=order, 5=family, and 6=genus. The 
# second argument is either "Y" or "N" for whether you would like to include the 
# unclassified entries in your output. If you would like to get an idea of 
# how well classified your data is, please use the complementary script 
# "otu.stats.R". The third, fourth, and beyond amount of arguments are paths to 
# to various OTU files produced from the analysis software mothur. This is a 
# tab-delimited file of three columns: OTU, size, and taxonomy. Note that the 
# taxonomy must span from domain through genus, leaving any unknowns as 
# 'unclassified'. 
#
# Please refer to the OTU section of this SOP from the authors of mothur for
# more details on how to generate the file: http://www.mothur.org/wiki/454_SOP
#
# Example of how to plot at the phylum taxonomic level, without unclassified 
# entries, and three different files: 
# Rscript plot.otu.single.R 2 "N" "/path.to.my.file" "/path.to.my.file2" "/path.to.my.file3"
#
# Author: James Matsumura

# Accept command line parameters
args<-commandArgs(TRUE)

# Load library to help with plotting
library("ggplot2")
library("reshape2")

# Assign args to variables
tax.level <- as.numeric(args[1])
class.or.unclass <- args[2]
file.path <- args[3:length(args)]

# Calculate the number of samples present
number.of.samples <- length(file.path)

# Initialize variables that will store the necessary information from
# each file as they are parsed through.
sample.freqs <- vector()
sample.class <- vector()

# Build labels for the data.frame 
label.samples <- vector()
label.samples.final <- vector()

# Iterate through each file, 
for(i in 1:number.of.samples){
  
  # Read in the file and the convert to data frame
  data <- read.table(file=file.path[i], header=T)
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
  
  sample.freqs <- append(sample.freqs, final.data$Count)
  sample.class <- append(sample.class, as.character(final.data$Classification))
  num.of.s <- rep("S ", length(final.data$Count))  
  label.samples <- paste(num.of.s, sep="", i)
  label.samples.final <- append(label.samples.final, as.character(label.samples))
}

df <- data.frame(sample=as.character(label.samples.final), class=as.character(sample.class), count=sample.freqs)

# Format the data for ggplot
mdf <- melt(df, id=c("sample","class","count"))

pdf("output.plot.otu.multiple.pdf", width = 9, height = 8)

ggplot(mdf, aes(x = sample, y = count, fill = class, order = class)) + 
  geom_bar(stat = 'identity', position = 'fill') + 
  xlab("Samples") + ylab("Percent Composition") +
  guides(fill=guide_legend(title=NULL)) + scale_colour_hue(l=80, c=150)
