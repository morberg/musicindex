# Creating index for Ultimate Broadway Fakebook

`tesseract` did not produce good results with this file. Alternative method:

1. Make a screenshot of the index files on the iPad. You will now have `IMG_0024.PNG`, `IMG_0025.PNG`, and `IMG_0026.PNG`
2. Create a PDF of these three files on you Mac by opening them in Preview and export to PDF: `ubf1.pdf`, `ubf2.pdf`,
   and `ubf3.pdf`
3. Convert the three PDF:s to text using [Google's Document AI](https://cloud.google.com/document-ai) in your browser.
   (I could not convert one single PDF created in Preview by printing to a file)
4. Select the tab *JSON* and download the results to `response1.json`, `response2.json`, `response3.json`
5. Run `python parse-ubf.py`. This will create `ubf-raw.csv`
6. Manually correct any errors in `ubf-raw.csv` and save as `ultimate-broadway-fake.csv` (there shouldn't be many)
7. Done

Note: the song Preludium on page 389 has subsongs that will not be listed in the index. Need to add a special case to
parse them properly.
