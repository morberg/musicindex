# Convert index.txt to csv for "The Best Fake Book Ever"
# Input format is a section: Line begins with '#' and then the section name.
# After that follows two columns: page title, separated by space until the next section or end of file
# Output format is three columns: "title",page,section
# Usage: awk -f index2csv.awk inputfile
BEGIN {ORS=""}

{
    if (/^#/)
    {
        section = ""
        for (i = 2; i<NF; ++i)
            section = section $i " "
        section = section $NF "\n"
    }
    else
    {   
        print "\""
        for (i=2; i<NF; ++i)
            print $i " "
        print $NF "\"," $1 "," section
    }
}