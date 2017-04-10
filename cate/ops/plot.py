# The MIT License (MIT)
# Copyright (c) 2016, 2017 by the ESA CCI Toolbox development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Description
===========

CLI/API data visualization operations

Components
==========

## plot_map

Plots a geospatial data slice on a world map. General python prompt usage:

```python
import matplotlib.pyplot as plt
from cate.ops.plot import plot_map

plot_map(dset)
plt.show()
```

General jupyter notebook usage:
```python
import matplotlib.pyplot as plt
from cate.ops.plot import plot_map

%matplotlib inline
plot_map(dset)
```
If a file path is given, the plot is saved.
Supported formats: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg,
svgz, tif, tiff

"""

import matplotlib
import xarray as xr

matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

from cate.core.op import op, op_input
from cate.core.types import VarName, PolygonLike


@op(tags=['graphical', 'plot', 'map'], no_cache=True)
@op_input('ds')
@op_input('var', value_set_source='ds', data_type=VarName)
@op_input('region', data_type=PolygonLike)
def plot_map(ds: xr.Dataset,
             var: VarName.TYPE = None,
             time=None,
             region: PolygonLike.TYPE = None,
             file: str = None) -> None:
    """
    Plot the given variable from the given dataset on a map with coastal lines.
    In case no variable name is given, the first encountered variable in the
    dataset is plotted. In case no time index is given, the first time slice
    is taken. It is also possible to set extents of the plot. If no extents
    are given, a global plot is created.

    The plot can either be shown using pyplot functionality, or saved,
    if a path is given. The following file formats for saving the plot
    are supported: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg,
    svgz, tif, tiff

    :param ds: xr.Dataset to plot
    :param var: variable name in the dataset to plot
    :param time: time slice index to plot
    :param region: Region to plot. If the region is not rectangular, it's
    bounding box will be used.
    :param file: filepath where to save the plot
    """
    if not isinstance(ds, xr.Dataset):
        raise NotImplementedError('Only raster datasets are currently '
                                  'supported')

    if not var:
        for key in ds.data_vars.keys():
            var = key
            break
    else:
        var = VarName.convert(var)

    if not time:
        time = 0

    if region is None:
        lat_min = -90.0
        lat_max = 90.0
        lon_min = -180.0
        lon_max = 180.0
    else:
        region = PolygonLike.convert(region)
        lon_min, lat_min, lon_max, lat_max = region.bounds

    if not _extents_sane(lat_min, lat_max, lon_min, lon_max):
        raise ValueError('Provided plot extents do not form a valid bounding box '
                         'within [-90.0,90.0,-180.0,180.0]')

    extents = [lon_min, lon_max, lat_min, lat_max]

    try:
        array_slice = ds[var].isel(time=time)
    except ValueError:
        array_slice = ds[var]
    fig = plt.figure(figsize=(16, 8))
    import cartopy.crs as ccrs
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extents, ccrs.PlateCarree())

    ax.coastlines()
    array_slice.plot.contourf(ax=ax, transform=ccrs.PlateCarree())

    if file:
        fig.savefig(file)


@op(tags=['graphical', 'plot', '1D'], no_cache=True)
@op_input('var', value_set_source='ds', data_type=VarName)
def plot_1D(ds: xr.Dataset, var: VarName.TYPE, file: str = None) -> None:
    """
    Plot a 1 dimensional variable, optionally save the figure in a file.

    The plot can either be shown using pyplot functionality, or saved,
    if a path is given. The following file formats for saving the plot
    are supported: eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg,
    svgz, tif, tiff

    :param ds: Datase from which to create a plot
    :param var: Variable to plot
    :param file: Filepath where to save the plot
    """
    var = VarName.convert(var)
    fig = plt.figure(figsize=(16, 8))
    ds[var].plot()

    if file:
        fig.savefig(file)


def _extents_sane(lat_min: float,
                  lat_max: float,
                  lon_min: float,
                  lon_max: float) -> bool:
    """
    Check if the provided [lat_min, lat_max, lon_min, lon_max] extents
    are sane.
    """
    if lat_min >= lat_max:
        return False

    if lon_min >= lon_max:
        return False

    if lat_min < -90.0:
        return False

    if lat_max > 90.0:
        return False

    if lon_min < -180.0:
        return False

    if lon_max > 180.0:
        return False

    return True
