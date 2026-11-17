WMS Downloader
==============

Downloads large georeferenced images from a [WMS](https://www.ogc.org/standard/wms/) service in tiles and combines them into one virtual raster.

WMS services usually limit the size of a single image. `wms-downloader` splits a large bounding box into square tiles and downloads each tile with a separate `GetMap` request. It then creates a [GDAL VRT](https://gdal.org/en/stable/drivers/raster/vrt.html) file, which can be opened as one image in e.g. QGIS or converted with `gdal_translate`.

Setup
-----

```
pip install wms-downloader                                       # from PyPI
pip install git+https://github.com/codeforberlin/wms-downloader  # directly from GitHub
```

Creating the VRT file requires `gdalbuildvrt` from [GDAL](https://gdal.org), which needs to be installed separately, e.g. with `brew install gdal` or `apt install gdal-bin`.

Usage
-----

Create a `config.yml` specifying your setup, e.g. for the true orthophotos of Berlin from 2024:

```yml
service:
  version: 1.1.1
  url: https://gdi.berlin.de/services/wms/truedop_2024
  srs: EPSG:25833
  format: jpeg
  transparent: false
  layer: truedop_2024

bbox:
  west:   360000.0
  south: 5790000.0
  east:   420000.0
  north: 5840000.0

size: 10000
resolution: 5000
timeout: 300
projection: EPSG:25833
directory: images
vrtfile: tiles.vrt
```

where:

* `service` describes the WMS service:
  * `version` is the WMS version, `1.1.1` or `1.3.0`,
  * `url` is the URL of the service, without query parameters,
  * `srs` is the projection used for the requests,
  * `format` is the image format, e.g. `jpeg` or `png`, which is also used as file extension,
  * `transparent` sets whether the background should be transparent (only for `png`), and
  * `layer` is the name of the layer,
* `bbox` is the bounding box for the map you want to retrieve, in the units of `projection`,
* `size` is the edge length of a single tile, in the units of `projection`,
* `resolution` is the width and height of a single tile in pixels,
* `timeout` is the timeout for a single request in seconds,
* `projection` is the projection of the downloaded images and the VRT file,
* `directory` is the directory where the downloaded images are stored, and
* `vrtfile` is the path to the created VRT file.

The example covers Berlin with 6 × 5 tiles of 10 × 10 km and 5000 × 5000 pixels, i.e. 30 requests with 2 m per pixel.

Then run the script with the `config.yml` as argument:

```
wms-downloader config.yml
```

Each tile is stored in `directory` as `<west>_<south>_<resolution>.<format>`, together with an `.aux.xml` file containing its georeference. Tiles which already have an `.aux.xml` file are skipped, so an interrupted download can simply be started again. The VRT file is only created if it does not exist yet, so delete it after downloading additional tiles.
