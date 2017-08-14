wms-downloader
==============

Install
-------

```bash
pip install wms-downloader
```

Usage
-----

Create a `config.yml` specifying your setup like this:

```yml
service:
  version: 1.1.1
  url: http://fbinter.stadt-berlin.de/fb/wms/senstadt/k_luftbild1953?
  srs: EPSG:25833
  format: jpeg
  layer: 0
bbox:
  west:   370000.0
  south: 5800000.0
  east:   415000.0
  north: 5837000.0

size: 10000
resolution: 600
timeout: 300
projection: EPSG:25833
directory: images
vrtfile: tiles.vrt
tmpfile: /tmp/wms.xml
```

where:

* `service` describes the used WMS service,
* `bbox` is the bounding box for the map you want to retrieve,
* `size` is the size of an individual TIFF file in the use projection,
* `resolution` is the resolution of an individual file in pixel,
* `directory` is the directory where the downloaded images are stored,
* `vrtfile` is the path to the created vrt file, and
* `tmpfile` is the path to the (temporary) xml file used for the WMS requests.

Then run the script with the `config.yml` as argument:

```
wms-downloader config.yml
```

Help
----

```
$ wms-downloader --help
usage: Downloads large geo TIFF files from a WMS service.

positional arguments:
  config      config file

optional arguments:
  -h, --help  show this help message and exit
```
