# concrete

Procedurally generated concrete poetry.

That is, a dressed up image-to-text converter I made to learn some basics. The program:

* selects random animals from a static list in Darius Kazemi's [Corpora](https://github.com/dariusk/corpora) project;
* rearranges each word based on the "[density](https://web.archive.org/web/20170604073704/https://dboikliev.wordpress.com/2013/04/20/image-to-ascii-conversion/)" of its characters (e.g. seal → slea);
* finds a random image of the animal with Google's [JSON/Atom Custom Search API](https://developers.google.com/custom-search/json-api/v1/overview);
* maps the characters to pixel intensities with code from Christian Diener's [asciinator.py](https://gist.github.com/cdiener/10567484); and
* parses these "poems" into HTML that is rendered as a PDF file with [wkhtmltopdf](https://wkhtmltopdf.org/).

See the [example output](https://github.com/nmifsud/concrete/raw/master/concrete-170914-235525.pdf).