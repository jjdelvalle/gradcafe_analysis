# GradCafe Analysis

This is an attempt at analyzing `gradcafe` data looking back and trying to make predictions on how the F21 cycle will turn out.

### NOTE

The COVID situation might change the behavior or grad admissions this year a lot, so these predictions might not be great.

## Usage

### Scraping

You might wanna analyze non-CS data. To do that you will have to scrape gradcafe results yourself using the `scrape_site.py` script.

`python scrape_site.py [search term] [number-of-pages]`

Where `search term` is the actual term you would use on GradCafe to find your data; `number-of-pages` would be the number of result pages you get **when you display 250 results per page**.

What I used to get CS data was the following:

`python scrape_site.py computer 257`

Could have just as well been:

`python scrape_site.py computer science 257`

### Parse the scraped files

This will create a directory with the name of your search query. HTML scraped files will be written in sequential order i.e. `1.html`, `2.html`, etc.

Then you will have to run the `parse_html` script in order to process the HTML scraped files and get a usable CSV file which you can then use to analyze whatever you wish. Its functionality is as follows:

`python parse_html.py [path_to_directory_with_html_files] [title_of_csv] [number_pages]`

A more concrete example would be therefore:

`python parse_html.py data/computer cs 257`

Where `data/computer` is the path of the directory holding the sequential HTML files. `cs` would be the name of the CSV file inside the `data` directory, and `257` is how many pages you scraped for this search.

### Analyze the resulting CSV and have fun

Finally, use the `GradAnalysis.ipynb` notebook to generate stats for a specific school and/or program:

```
get_uni_stats(dataframe_of_reports,
				search='search terms',
				title='Title for graph',
				degree='degree',
				field='field')

```

e.g.: 

`get_uni_stats(df_1620, 'berkeley', 'UC Berkeley', 'PhD', 'CS')`

Which results in this image of various stats:

![sample result](app/output/UC%20Berkeley_CS%20PhD.png)

## Shoutouts

I am standing on the shoulders of these posts:

* https://debarghyadas.com/writes/the-grad-school-statistics-we-never-had/
* https://github.com/deedy/gradcafe_data
* https://www.reddit.com/r/gradadmissions/comments/7srxxy/decision_timelines_for_particular_universities/

