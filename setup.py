from setuptools import setup, find_packages

from wms_downloader import (
    __title__ as title,
    __version__ as version,
    __author__ as author,
    __license__ as license
)

description = 'Downloads large geo TIFF files from a WMS service.'
email = 'jochenklar@gmail.com'
url = 'https://github.com/jochenklar/wms-downloader'

requirements = [
    'mercantile',
    'PyYAML',
    'numpy'
]

scripts = [
    'bin/wms-downloader'
]

setup(
    name=title,
    version=version,
    description=description,
    url=url,
    author=author,
    author_email=email,
    maintainer=author,
    maintainer_email=email,
    license=license,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[],
    scripts=scripts,
)
