"""
concrete.py

Procedurally generated concrete poetry.

Copyright 2018 Nathan Mifsud <nathan@mifsud.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import io
import numpy as np
import pdfkit
import random
import requests
import sys
import time
from googleapiclient.discovery import build
from PIL import Image
from pycorpora import animals

# Ask for the desired number of poems if not specified with an input argument.
if len(sys.argv) != 2:
    num_poems = int(input('\nHow many poems? '))
else:
    num_poems = int(sys.argv[1])

# Create a random list of animal species from an existing corpus.
# See: https://github.com/aparrish/pycorpora
species = random.sample(animals.common['animals'], num_poems)

# Define parameters to enable a custom Google search. This requires a personal
# JSON/Atom Custom Search API key.
# See: https://developers.google.com/custom-search/json-api/v1/overview
service = build('customsearch', 'v1',
                developerKey='key')

# This loop iterates through the species names, rearranges the letters so that
# the 'darkness' of each letter can be mapped to image pixel intensities, grabs
# relevant image URLs, and then parses an image per species into text.
poems, passed = [], []
for p in range(num_poems):
    # Prepare a character set for later use by removing first stripping spaces
    # that appear in some species names (e.g. grizzly bear).
    stripped = species[p].replace(' ', '')
    # Sort the constituent letters according to a predefined weight order (from
    # the least to the most dense characters).
    alphabet = 'czrsivtlxfeajonuykpwhqbdmg'
    weighted = sorted(list(stripped),
                      key=lambda word: [alphabet.index(c) for c in word])
    # Prepend blank spaces to the final character set. These will later replace
    # the lightest image pixels, sometimes producing a better animal silhouette.
    set = np.asarray(list('  ' + ''.join(weighted)))

    # Query Google for image URLs. This requires a Custom Search Engine ID (see
    # https://cse.google.com) in the 'cx' parameter. I append 'transparent' to
    # the search query to increase the likelihood of grabbing images that will
    # produce recognisable final output, given that when rendered as text,
    # complex backgrounds can be hard to separate from the animals themselves.
    r = service.cse().list(
        q=(species[p] + ' transparent'),
        cx='cx',
        searchType='image',
        num=10,
        imgSize='medium'
    ).execute()
    images = []
    for item in r['items']:
        images.append(item['link'])
    # Shuffle the resulting list of image URLs to reduce the predictability of
    # the results in the event that this program is run multiple times.
    random.shuffle(images)

    # This subloop attempts to convert the image pixels into text for as many
    # iterations as it takes for the number of successfully converted ('passed')
    # images to match the desired number of poems. Sometimes exceptions occur
    # because the image data is not as required (e.g. certain file formats
    # don't work), which is why the program pulled 10 URLs for each search
    # query in the previous step. An exception handler allows it to continue
    # down the list of URLs until one works.
    attempt = 0
    while len(passed) < p + 1:
        try:
            # Put the image data into a variable.
            r = requests.get(images[attempt])
            r.content
            i = Image.open(io.BytesIO(r.content))

            # Set the dimensions of the output poem using the aspect ratio of
            # the original image, skewed in width to correct for the fact that
            # letters are narrow rather than pixel-square.
            maxSide, skew = 40, 7 / 4
            ratio = min(maxSide / i.size[0], maxSide / i.size[1])
            newSize = (round(i.size[0] * skew * ratio),
                       round(i.size[1] * ratio))

            # The following 4 lines of code were adapted from Christian Diener.
            # See: https://gist.github.com/cdiener/10567484
            # First, sum the RGB values of each pixel in the resized image.
            i = np.sum(np.asarray(i.resize(newSize)), axis=2)
            # Then scale the resulting overall intensity values to zero.
            i -= i.min()
            # Map each value of the image matrix to the character set.
            i = (1.0 - i / i.max()) * (set.size - 1)
            # Create a continuous letter string, with each row (r) of pixels
            # separated by line breaks (<br>), and append to the list of poems.
            poems.append('<br>'.join((''.join(r) for r in set[i.astype(int)])))

            # Keep track of the successful attempts.
            passed.append(images[attempt])
            print('\nRendered ' + species[p])

        except Exception as e:  # Note failed attempts and try again.
            attempt += 1
            print('\nError\t' + images[p] + '\n\t', end='')
            print(e)

# Assemble the HTML and produce a PDF file, formatted by an external CSS file.
# See: https://wkhtmltopdf.org/
file = 'concrete-' + time.strftime('%y%m%d-%H%M%S') + '.pdf'
css = 'concrete.css'
options = {'margin-top': '1in', 'margin-bottom': '1in',
           'margin-left': '1in', 'margin-right': '1in',
           'encoding': 'utf-8', 'no-outline': None, 'quiet': None}
text = ('<h1>concrete animals</h1><p>https://github.com/nmifsud/concrete</p>'
        + '<p>generated on ' + time.strftime('%d %b %Y at %#H:%M:%S') + '</p>'
        + '<br><p>featured in this edition:</p><ul>')
for p in range(num_poems):
    text += '<li>' + species[p] + '</li>'
text += '</ul>'
for p in range(num_poems):
    text += '<h2>' + species[p] + '</h2><p>' + poems[p] + '</p>'
text = text.replace(' ', '&nbsp;')  # Necessary to preserve whitespace.
pdfkit.from_string(text, file, css=css, options=options)
print('\nGenerated ' + file)
