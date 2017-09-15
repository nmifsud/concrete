"""
concrete.py

Procedurally generated concrete poetry.

Copyright 2017 Nathan Mifsud <nathan@nmifsud.com>

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

# check for command line argument
if len(sys.argv) != 2:
    num_poems = int(input('\nHow many poems? '))
else:
    num_poems = int(sys.argv[1])

# select random words from corpus in https://github.com/dariusk/corpora
subjects = random.sample(animals.common['animals'], num_poems)

poems, passed = [], []
service = build('customsearch', 'v1',
    developerKey='key') # requires JSON/Atom Custom Search API key
    
for p in range(num_poems):
    # prep character set for later use
    sSubject = subjects[p].replace(' ', '') # for multi-word animals
    alphabet = 'czrsivtlxfeajonuykpwhqbdmg' # sort according to 'density'
    wSubject = sorted(list(sSubject),
        key=lambda word: [alphabet.index(c) for c in word])
    set = np.asarray(list('  '+''.join(wSubject)))
    
    # query Google for image URLs
    r = service.cse().list(
        q=(subjects[p]+' transparent'), # for recognisable final output
        cx='cx', # Custom Search Engine ID, see https://cse.google.com
        searchType='image',
        num=10,
        imgSize='medium'
    ).execute()
    images = []
    for item in r['items']:
        images.append(item['link'])
    random.shuffle(images) # reduce predictability of results
    
    attempt = 0
    while len(passed) < p+1:
        try:
            # put image data into variable
            r = requests.get(images[attempt])
            r.content
            i = Image.open(io.BytesIO(r.content))
            
            # set final output size skewed to compensate for narrow letters
            maxSide, skew = 40, 7/4
            ratio = min(maxSide/i.size[0], maxSide/i.size[1])
            newSize = (round(i.size[0]*skew*ratio),round(i.size[1]*ratio))
            
            # code adapted from https://gist.github.com/cdiener/10567484
            i = np.sum(np.asarray(i.resize(newSize)),axis=2) # sum RGB pixels
            i -= i.min() # scale intensity values
            i = (1.0 - i/i.max())*(set.size-1) # map values to character set
            poems.append('<br>'.join((''.join(r) for r in set[i.astype(int)])))
            passed.append(images[attempt])
            print('\nRendered '+subjects[p])
            
        except Exception as e: # note failed attempts and try again
            attempt = attempt+1
            print('\nError\t'+images[p]+'\n\t', end='')
            print(e)

# assemble HTML and output as PDF file
file = 'concrete-'+time.strftime('%y%m%d-%H%M%S')+'.pdf'
css = 'concrete.css'
options = {'margin-top': '1in', 'margin-bottom': '1in',
    'margin-left': '1in', 'margin-right': '1in',
    'encoding': 'utf-8', 'no-outline': None, 'quiet': None}
text = ('<h1>concrete animals</h1><p>https://github.com/nmifsud/concrete</p>'
    +'<p>generated on '+time.strftime('%d %b %Y at %#H:%M:%S')+'</p>'
    +'<br><p>featured in this edition:</p><ul>')
for p in range(num_poems):
    text = text+'<li>'+subjects[p]+'</li>'
text = text+'</ul>'
for p in range(num_poems):
    text = text+('<h2>'+subjects[p]+'</h2><p>'+poems[p]+'</p>')
text = text.replace(' ', '&nbsp;') # preserve whitespace
pdfkit.from_string(text, file, css=css, options=options)
print('\nGenerated '+file)