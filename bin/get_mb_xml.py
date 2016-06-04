#!/usr/bin/env python
from urllib.request import urlopen
import lxml.etree as etree
#
# options - both required
# --discid
# --output

discid="PC1Qqz2HaZOx5SxP9UeMiVbQexo-"
url="http://musicbrainz.org/ws/2/discid/{0}?inc=recordings".format(discid)
response = urlopen(url)
x = etree.fromstring(response.read())
with open(outputfile,'w') as fh:
    fh.write( etree.tostring(x, pretty_print = True))


