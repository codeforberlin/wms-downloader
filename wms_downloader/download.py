from __future__ import print_function

import argparse
import glob
import os
import subprocess
import yaml
import logging

logger = logging.getLogger(__name__)

xml_template = '''<GDAL_WMS>
  <Service name="WMS">
    <Version>%(version)s</Version>
    <ServerUrl>%(url)s</ServerUrl>
    <SRS>%(srs)s</SRS>
    <ImageFormat>image/%(format)s</ImageFormat>
    <Layers>%(layer)s</Layers>
    <transparent>%(transparent)s</transparent>
  </Service>
  <DataWindow>
    <UpperLeftX>%(west)s</UpperLeftX>
    <UpperLeftY>%(north)s</UpperLeftY>
    <LowerRightX>%(east)s</LowerRightX>
    <LowerRightY>%(south)s</LowerRightY>
    <SizeX>%(resolution)s</SizeX>
    <SizeY>%(resolution)s</SizeY>
  </DataWindow>
  <Timeout>%(timeout)s</Timeout>
  <Projection>%(projection)s</Projection>
  <BandsCount>%(bandscount)s</BandsCount>
</GDAL_WMS>'''


def main():
    parser = argparse.ArgumentParser(usage='Downloads large geo TIFF files from a WMS service.')
    parser.add_argument('config', help='config file')
    parser.add_argument('--debug', action='store_true', help='debug output')
    args = parser.parse_args()

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    with open(args.config) as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    create_directory(config)
    download_images(config)
    create_vrt_file(config)


def create_directory(config):
    try:
        os.makedirs(config['directory'])
        logger.debug('directory "%s" created', config['directory'])
    except OSError:
        logger.debug('directory "%s" exists', config['directory'])


def download_images(config):
    west_range = list(arange(config['bbox']['west'], config['bbox']['east'], config['size']))
    south_range = list(arange(config['bbox']['south'], config['bbox']['north'], config['size']))

    for west in west_range:
        for south in south_range:
            filename = os.path.join(config['directory'], '%(west)s_%(south)s_%(resolution)s.gdal.%(format)s' % {
                'west': west,
                'south': south,
                'resolution': config['resolution'],
                'format': config['service']['format']
            })

            if not os.path.exists(filename + '.aux.xml'):
                print('fetching %s' % filename)
                xml_params = {
                    'west': west,
                    'south': south,
                    'east': west + config['size'],
                    'north': south + config['size'],
                    'resolution': config['resolution'],
                    'timeout': config['timeout'],
                    'projection': config['projection'],
                    'transparent': config['service']['transparent'],
                    'bandscount': config['bandscount']
                }
                xml_params.update(config['service'])

                with open(config['tmpfile'], 'w') as f:
                    f.write(xml_template % xml_params)

                logger.info('fetching "%s"', filename)
                args = ['gdal_translate', '-of', config['service']['format'], config['tmpfile'], filename]
                subprocess.check_call(args)


def create_vrt_file(config):
    if not os.path.exists(config['vrtfile']):
        args = ['gdalbuildvrt', '-a_srs', config['projection'], config['vrtfile']]
        args += glob.glob('%s/*.gdal.%s' % (config['directory'],config['service']['format']) )
        subprocess.check_call(args)


def arange(start, stop, step):
    current = start
    while current < stop:
        yield current
        current += step

if __name__ == "__main__":
    main()
