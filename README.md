# QQuake, a plugin for loading seismological data in QGIS

QQuake plugin is a plugin that facilitates the download of seismological data
from different sources and load them directly into QGIS.

More information at the QQuake homepage at<br>
https://www.emidius.eu/qquake/

The following is a scientific paper describing the plugin and the context that led to its development

Locati M., Vallone R., Ghetta M. and Dawson N. (2021). QQuake, a QGIS Plugin for Loading Seismological Data From Web Services. Front. Earth Sci. 9:614663. https://doi.org/10.3389/feart.2021.614663

If you want to try the latest, unstable version, you have to download the source code from this repository, create a zip file with the content of the "qquake" folder, and install the plugin from the zip file in QQuake.
For example, in the Linux terminal, you may follow this procedure to create the zip file
```
$ mkdir qquake_test
$ cd qquake_test
$ wget https://github.com/INGV/qquake/archive/refs/heads/master.zip
$ unzip master.zip
$ cd qquake-master
$ zip -r qquake_test.zip qquake
```
And then, install the plugin selecting "qquale_test.zip" in QQGIS.
