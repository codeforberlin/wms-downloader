import argparse
import subprocess
from pathlib import Path

import requests
import yaml
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

# GDAL reads the georeference of a plain JPEG/PNG from this sidecar file (<image>.aux.xml)
aux_xml_template = """<PAMDataset>
  <SRS>{srs}</SRS>
  <GeoTransform>{west}, {pixel_size}, 0.0, {north}, 0.0, -{pixel_size}</GeoTransform>
</PAMDataset>
"""


def create_progress():
    return Progress(
        TextColumn('{task.description}', markup=False),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )


def main():
    parser = argparse.ArgumentParser(description='Downloads large geo TIFF files from a WMS service.')
    parser.add_argument('config', help='config file')
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())

    download_images(config)
    create_vrt_file(config)


def download_images(config):
    service = config['service']

    directory = Path(config['directory'])
    directory.mkdir(parents=True, exist_ok=True)

    west_range = list(arange(config['bbox']['west'], config['bbox']['east'], config['size']))
    south_range = list(arange(config['bbox']['south'], config['bbox']['north'], config['size']))

    with create_progress() as progress:
        task = progress.add_task(f'Downloading to {directory}', total=len(west_range) * len(south_range))
        for west in west_range:
            for south in south_range:
                file_path = directory / f'{west}_{south}_{config["resolution"]}.{service["format"]}'
                aux_path = file_path.with_name(file_path.name + '.aux.xml')

                # the .aux.xml file is written last, so it marks a complete download
                if not aux_path.exists():
                    east, north = west + config['size'], south + config['size']
                    response = requests.get(
                        service['url'],
                        params={
                            'SERVICE': 'WMS',
                            'VERSION': service['version'],
                            'REQUEST': 'GetMap',
                            'LAYERS': service['layer'],
                            'STYLES': '',
                            # WMS 1.3.0 renamed SRS to CRS
                            'CRS' if service['version'] == '1.3.0' else 'SRS': service['srs'],
                            'BBOX': f'{west},{south},{east},{north}',
                            'WIDTH': config['resolution'],
                            'HEIGHT': config['resolution'],
                            'FORMAT': f'image/{service["format"]}',
                            'TRANSPARENT': str(service['transparent']).upper(),
                        },
                        headers={'User-Agent': 'wms-downloader'},
                        timeout=config['timeout'],
                    )
                    response.raise_for_status()

                    # WMS services report errors with status 200 and an XML document instead of an image
                    content_type = response.headers.get('Content-Type', '')
                    if not content_type.startswith('image/'):
                        raise RuntimeError(f'Expected an image for {file_path}, got {content_type}:\n{response.text}')

                    file_path.write_bytes(response.content)
                    aux_path.write_text(
                        aux_xml_template.format(
                            srs=config['projection'],
                            west=west,
                            north=north,
                            pixel_size=config['size'] / config['resolution'],
                        )
                    )

                progress.advance(task)


def create_vrt_file(config):
    vrt_path = Path(config['vrtfile'])
    if not vrt_path.exists():
        file_paths = sorted(Path(config['directory']).glob(f'*.{config["service"]["format"]}'))
        args = ['gdalbuildvrt', '-a_srs', config['projection'], str(vrt_path), *map(str, file_paths)]
        subprocess.check_call(args)


def arange(start, stop, step):
    current = start
    while current < stop:
        yield current
        current += step
