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

Then run the script in the same directory as `config.yml` or use the `-c` argument:

```
    wms-downloader
    wms-downloader -c /path/to/my_custom_config.yml
```
