# How to generate index.csv from images
## Using scanned images
This workflow works nicely for the 10 index pages for "The Best Fake Book Ever" from Hal Leonard. It can be improved
significantly. Adjust as needed.

First take screenshots of the index pages on an iOS device. Transfer to your computer. Then run `tesseract` to do OCR on
the PNG images and convert them to text. In fish shell:

```
for i in *.png
    tesseract --dpi 252 $i stdout >>ocr.txt
end
```

Next we work on the text to convert it to a properly formatted CSV file. Begin to manually modify the `ocr.txt` file to
remove errors from OCR. We will fix some errors later on, but not all. Save this file as `manual-cleanup.txt`. Create
sections by starting a line with `#` followed by the name of the section.

Run this command on your semi-clean file:

```
grep -v '22:16' manual-cleanup.txt |awk -v ORS=' ' 'NR>1 && /^[0-9]/{print "\n"} NF' |gsed 's/|/I/g; s/ #/\n#/; s/\s*$//' >index.txt
```
What is happening here?

`grep`: Removes timestamp from screenshot

`awk`: [Merges multiple lines](https://stackoverflow.com/questions/42237708/join-lines-depending-on-the-line-beginning) to one (will leave extra space at beginning and end)

`gsed`: Removes whitespace in beginning, change | to I, put Sections (lines beginning with #) on a line of their own, remove trailing whitespace

Finally run:
```
awk -f ../scripts/index2csv.awk index.txt >index.csv
```

to generate `index.csv` which can then be imported to forScore. First field is *title*, second is *start page*, and
third is *tag* in forScore.

## Other useful commands
### Data pasted from Excel
If you copy two columns (one with the title and one with the page number) from Excel and paste them to a text document
you will get the title followed by some white space and then the page number. This sed incantation will enclose the
first column in quotes, remove unnecessary whitespace, and add a comma between the columns.
```
sed -E 's/(.*)[[:space:]]([0-9]+)/"\1",\2/'
```

### Merging two lines to one
```
cat file.txt |paste -d " " - -
```