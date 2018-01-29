# concrete

Procedurally generated [concrete poetry](https://en.wikipedia.org/wiki/Concrete_poetry).

I was inspired by Lewis Thomas's [wonderful comparison](http://www.nejm.org/doi/pdf/10.1056/NEJM197211092871910) between human speech and the pursuits of social insects:

> Language is, like nest building or hive making, the universal and biologically specific activity of human beings. We engage in it communally, compulsively, and automatically. We cannot be human without it; if we were to be separated from it our minds would die, as surely as bees lost from the hive.
>
> [&hellip;] New ways of stringing words and sentences together come into fashion and vanish again, but the underlying structure simply grows, enriches itself, and expands.

Ant nests accrete from the tiny bits of earth that each worker carries in its mandibles. Here, sculptural forms are shaped by the dirt clods of language—the letters of our alphabet.

Each time it is run, the program:
* selects random animal species from a static list in Darius Kazemi's [Corpora](https://github.com/dariusk/corpora) project;
* sorts the letters in each species according to [character density](https://web.archive.org/web/20170604073704/https://dboikliev.wordpress.com/2013/04/20/image-to-ascii-conversion/) (e.g. seal → slea);
* finds a random image of each species using Google's [JSON/Atom Custom Search API](https://developers.google.com/custom-search/json-api/v1/overview);
* maps the reordered letters to pixel intensities with code from [asciinator.py](https://gist.github.com/cdiener/10567484); and
* parses the resulting poems into HTML that is rendered as a PDF file with [wkhtmltopdf](https://wkhtmltopdf.org/).

You can see example output [here](https://github.com/nmifsud/concrete/blob/master/concrete-170914-235525.pdf) and [here](https://github.com/nmifsud/concrete/blob/master/concrete-170914-230627.pdf).