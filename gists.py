# Main modules https://docs.obspy.org/packages/obspy.core.html

# metodo per leggere eventi da file o da url
# https://docs.obspy.org/packages/autogen/obspy.core.event.read_events.html
from obspy.core.event import read_events

# url preso da https://www.emidius.eu/FDSNeasy/
url = 'https://www.emidius.eu/fdsnws/event/1/query?eventid=quakeml:eu.ahead/event/18990105_0245_000&includeallorigins=true&includeallmagnitudes=true&format=xml'

l = read_events(url)

# è una lista (per adesso sempre di un elemento solo) di oggetti Catalog
# https://docs.obspy.org/packages/autogen/obspy.core.event.Catalog.html#obspy.core.event.Catalog
# ogni singolo elemento della lista, Catalog, è un dizionario

l.events

for k, v in l.events[0].items():
    print(k, v)

# la chiave 'origins' restituisce una lista di oggetti (anche qui uno solo) di
# oggetti Origin

print(b.events[0]['origins'])

# tramite Origin si ha accesso a informazioni vere su evento (lat, long, magnitudine, etc)

dir(b.events[0]['origins'][0])
b.events[0]['origins'][0].latitude

# vedi un elenco
for k, v in b.events[0]['origins'][0].items():
    print(k, v)

##############################################################################

import lxml.etree as ET
import xml.etree.ElementTree as ET
import urllib.request

opener = urllib.request.build_opener()
to_parse = opener.open(url)
url = 'https://www.emidius.eu/fdsnws/event/1/query?eventid=quakeml:eu.ahead/event/13270512_0000_000&includeallorigins=true&includeallmagnitudes=true&format=xml'

tree = ET.parse()



##############################################
# leggere CSV degli eventi da remoto e trasformali in un dizionario di liste
#


import csv
import urllib.request
from collections import defaultdict

text_url = 'http://service.iris.edu/fdsnws/event/1/query?starttime=2019-11-19T00:00:00&endtime=2019-11-19T23:59:59&minmag=4&maxmag=9&orderby=time-asc&limit=100&format=text'

with urllib.request.urlopen(text_url) as response:
    my_text = response.read().decode()

lines = my_text.splitlines()
d = defaultdict(list)
reader = csv.DictReader(lines, delimiter='|')
for row in reader:
    for k, v in row.items():
        d[k.strip()].append(v)



######### dizionario degli URL FDSN-Event per ogni WS

ws = {
    'AHEAD/SHEEC' : 'https://www.emidius.eu/fdsnws/event/1/query?',
    'INGV ASMI/CPTI' : 'https://emidius.mi.ingv.it/fdsnws/event/1/query?',
    'INGV ONT/ISIDe' : 'http://webservices.ingv.it/fdsnws/event/1/query?',
    'ETHZ SED' : 'http://arclink.ethz.ch/fdsnws/event/1/query?',
    'EMSC-CSEM' : 'http://www.seismicportal.eu/fdsnws/event/1/query?',
    'ORFEUS ESM' : 'http://esm.mi.ingv.it/fdsnws/event/1/query?',
    'ISC' : 'http://www.isc.ac.uk/fdsnws/event/1/query?',
    'ISC (IRIS mirror)' : 'http://isc-mirror.iris.washington.edu/fdsnws/event/1/query?',
    'IRIS' : 'http://service.iris.edu/fdsnws/event/1/query?',
    'USGS' : 'http://earthquake.usgs.gov/fdsnws/event/1/query?',
    'NCEDC' : 'http://service.ncedc.org/fdsnws/event/1/query?',
    'SCEDC' : 'http://service.scedc.caltech.edu/fdsnws/event/1/query',
}


https://www.emidius.eu/fdsnws/event/1/query?starttime=1000-01-01T23:59:59&endtime=1398-01-01T00:00:00&minmag=4.0&maxmag=9.0&limit=1000&format=text

https://www.emidius.eu/fdsnws/event/1/query?eventid=quakeml:eu.ahead/event/10050000_0000_000&includeallorigins=true&includeallmagnitudes=true&format=xml

https://www.emidius.eu/fdsnws/event/1/query?eventid=quakeml:eu.ahead/event/10380000_0000_000&includeallorigins=true&includeallmagnitudes=true&format=xml

previousMapTool = iface.mapCanvas().mapTool()
myMapTool = QgsMapToolEmitPoint( iface.mapCanvas() )
# create the polygon rubber band associated to the current canvas
myRubberBand = QgsRubberBand( iface.mapCanvas(), QgsWkbTypes.PolygonGeometry )
# set rubber band style
color = QColor("red")
color.setAlpha(50)
myRubberBand.setColor(color)

def showCoordinates( currentPos ):
    if myRubberBand and myRubberBand.numberOfVertices():
        myRubberBand.removeLastPoint()
        myRubberBand.addPoint( currentPos )

iface.mapCanvas().xyCoordinates.connect( showCoordinates )

def manageClick( currentPos, clickedButton ):
    if clickedButton == Qt.LeftButton:
        myRubberBand.addPoint( currentPos )
    # terminate rubber band editing session
    if clickedButton == Qt.RightButton:
        # remove showCoordinates map canvas callback
        iface.mapCanvas().xyCoordinates.disconnect( showCoordinates )
        # reset to the previous mapTool
        iface.mapCanvas().setMapTool( previousMapTool )
        # clean remove myMapTool and relative handlers
        myMapTool.deleteLater()
        # remove the rubber band from the canvas
        iface.mapCanvas().scene().removeItem(myRubberBand)
myMapTool.canvasClicked.connect( manageClick )
iface.mapCanvas().setMapTool( myMapTool )
