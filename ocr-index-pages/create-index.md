# How to generate index.csv from images

This workflow works nicely for the 10 index pages for "The Best Fake Book Ever" from Hal Leonard. Adjust as needed.

Begin with running `tesseract` to do OCR on the PNG images of the index pages and convert them to text. In fish shell:

```
for i in *.png
    tesseract --dpi 252 $i stdout >>ocr.txt
end
```

Next we work on the text to convert it to a properly formatted CSV file. Begin to manually modify the `ocr.txt` file to remove errors from OCR. We will fix some errors later on, but not all. Save this file as `manual-cleanup.txt`. Create sections by starting a line with `#` followed by the name of the section.

Run this command on your clean file:

```
grep -v '22:16' manual-cleanup.txt |awk -v ORS=' ' 'NR>1 && /^[0-9]/{print "\n"} NF' |gsed 's/|/I/g; s/ #/\n#/; s/\s*$//' >index.txt
```
What is happening here?

`grep`: Removes timestamp from screenshot

`awk`: [Merges multiple lines](https://stackoverflow.com/questions/42237708/join-lines-depending-on-the-line-beginning
) to one (will leave extra space at beginning and end)

`gsed`: Removes whitespace in beginning, change | to I, put Sections (lines beginning with #) on a line of their own, remove trailing whitespace

Finally run:
```
awk -f index2csv.awk index.txt|sed -E 's/ (,[0-9]+), /"\1,/; s/^ /"/' >index.csv
```

to generate `index.csv` which can then be imported to forScore. First field is *title*, second is *start page,* and third is *tag*.