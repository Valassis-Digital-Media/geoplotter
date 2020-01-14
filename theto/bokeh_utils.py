from bokeh.models import CheckboxGroup, CheckboxButtonGroup, RangeSlider, Slider, Dropdown, RadioButtonGroup
from bokeh.models import markers, WMTSTileSource
from bokeh.models.glyphs import MultiPolygons, Text

from .color_utils import assign_colors, check_color

# non-Google-Map map tile sources
# adapted from https://github.com/holoviz/holoviews/blob/master/holoviews/element/tiles.py


def get_tile_source(name):
    tiles = {
        # CartoDB basemaps
        'carto_dark': 'https://cartodb-basemaps-4.global.ssl.fastly.net/dark_all/{Z}/{X}/{Y}.png',
        'carto_eco': 'https://3.api.cartocdn.com/base-eco/{Z}/{X}/{Y}.png',
        'carto_light': 'https://cartodb-basemaps-4.global.ssl.fastly.net/light_all/{Z}/{X}/{Y}.png',
        'carto_midnight': 'https://3.api.cartocdn.com/base-midnight/{Z}/{X}/{Y}.png',

        # Stamen basemaps
        'stamen_terrain': 'https://tile.stamen.com/terrain/{Z}/{X}/{Y}.png',
        'stamen_terrain_retina':  'https://tile.stamen.com/terrain/{Z}/{X}/{Y}@2x.png',
        'stame_watercolor': 'https://tile.stamen.com/watercolor/{Z}/{X}/{Y}.jpg',
        'stamen_toner': 'https://tile.stamen.com/toner/{Z}/{X}/{Y}.png',
        'stamen_toner_background': 'https://tile.stamen.com/toner-background/{Z}/{X}/{Y}.png',
        'stamen_toner_labels':'https://tile.stamen.com/toner-labels/{Z}/{X}/{Y}.png',

        # Esri maps (see https://server.arcgisonline.com/arcgis/rest/services for the full list)
        'esri_imagery': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg',
        'esri_natgeo': 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{Z}/{Y}/{X}',
        'esri_usatopo': 'https://server.arcgisonline.com/ArcGIS/rest/services/USA_Topo_Maps/MapServer/tile/{Z}/{Y}/{X}',
        'esri_terrain': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{Z}/{Y}/{X}',
        'esri_reference': 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Reference_Overlay/MapServer/tile/{Z}/{Y}/{X}',

        # Miscellaneous
        'osm': 'https://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png',
        'osm_bw': 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png',
        'wikipedia': 'https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png'
    }

    if name is None:
        return list(tiles.keys())

    if name not in tiles:
        return None

    return WMTSTileSource(url=tiles[name])


# all supported models
MODELS = {k: getattr(markers, k) for k in markers.__all__}
MODELS['MultiPolygons'] = MultiPolygons
MODELS['Text'] = Text

MODELS_REVERSE = {v: k for k, v in MODELS.items()}

# all supported widgets
WIDGETS = {
    'Dropdown': Dropdown, 
    'RangeSlider': RangeSlider, 
    'CheckboxGroup': CheckboxGroup, 
    'CheckboxButtonGroup': CheckboxButtonGroup,
    'Slider': Slider,
    'RadioButtonGroup': RadioButtonGroup
}

# filter boilerplate
FILTERS = {
    'Dropdown': '''
        var indices = [];
        for (var i = 0; i <= source.data[reference].length; i++){
            if (source.data[reference][i] == widget.value) {
                indices.push(i)
            }
        }
        return indices;
    ''',
    'Slider': '''
        var indices = [];
        if (widget.step % 1 === 0){
            var value = Math.trunc(widget.value)
        } else {
            var value = widget.value
        }
        
        for (var i = 0; i <= source.data[reference].length; i++){
            if (source.data[reference][i] == widget.value) {
                indices.push(i)
            }
        }
        return indices;
    ''',
    'RangeSlider': '''
        var indices = [];
        if (widget.step % 1 === 0){
            var lower = Math.trunc(widget.value[0])
            var upper = Math.trunc(widget.value[1])
        } else {
            var lower = widget.value[0]
            var upper = widget.value[1]        
        }
        for (var i = 0; i <= source.data[reference].length; i++){
            var value = source.data[reference][i]
            if (value >= lower) {
                if (value <= upper) {
                    indices.push(i)
                }
            }
        }
        return indices;
    ''',
    'CheckboxGroup': '''
        var indices = [];
        var results = [];

        for (var i = 0; i < widget.active.length; i++)
            results.push(widget.labels[widget.active[i]]);

        for (var i = 0; i < source.data[reference].length; i++){
            var value_string = source.data[reference][i].toString()
            if (results.includes(value_string)) {
                indices.push(i)
            }
        }
        return indices;
    ''',
    'CheckboxButtonGroup': '''
        var indices = [];
        var results = [];

        for (var i = 0; i < widget.active.length; i++)
            results.push(widget.labels[widget.active[i]]);

        for (var i = 0; i < source.data[reference].length; i++){
            var value_string = source.data[reference][i].toString()
            if (results.includes(value_string)) {
                indices.push(i)
            }
        }
        return indices;
    ''',
    'RadioButtonGroup': '''
        var indices = [];
        var results = [];

        var result = widget.labels[widget.active];

        for (var i = 0; i < source.data[reference].length; i++){
            var value_string = source.data[reference][i].toString()
            if (result == value_string) {
                indices.push(i)
            }
        }
        return indices;
    '''
}

    
def auto_widget_kwarg(widget_type, kwarg, reference_array):
    """
    For a particular widget type, keyword argument, and array
    of values, set reasonable defaults.
    
    """
    
    if widget_type in ("CheckboxGroup", "CheckboxButtonGroup"):
        reference_set = list(set(reference_array))
        if kwarg == 'labels':
            return reference_set
        if kwarg == 'active':
            return [x for x in range(len(reference_set))]
        raise ValueError(
            'The only auto-populating kwargs for {} are `labels` and `active`.'.format(widget_type)
        )
    if widget_type == "RangeSlider":
        if kwarg == 'start':
            return min(reference_array)
        if kwarg == 'end':
            return max(reference_array)
        if kwarg == 'value':
            return min(reference_array), max(reference_array)
        raise ValueError(
            'The only auto-populating kwargs for {} are `start`, `end` and `value`.'.format(widget_type)
        ) 
    if widget_type == "Slider":
        if kwarg == 'start':
            return min(reference_array)
        if kwarg == 'end':
            return max(reference_array)
        if kwarg == 'value':
            return min(reference_array)
        raise ValueError(
            'The only auto-populating kwargs for {} are `start`, `end` and `value`.'.format(widget_type)
        )
    if widget_type == "Dropdown":
        reference_set = list(set(reference_array))
        if kwarg == 'menu':
            return reference_set
        if kwarg == 'value':
            return reference_set[0]
        raise ValueError(
            'The only auto-populating kwargs for {} are `menu` and `value`.'.format(widget_type)
        )    
    if widget_type in ("RadioButtonGroup", ):
        reference_set = list(set(reference_array))
        if kwarg == 'labels':
            return reference_set
        if kwarg == 'active':
            return 0
        raise ValueError(
            'The only auto-populating kwargs for {} are `labels` and `active`.'.format(widget_type)
        )
    
    raise NotImplementedError('Widget type `{}` not yet implemented.'.format(widget_type))

    
def prepare_properties(
    bokeh_model, kwargs, source_df, categorical_palette=None,
    start_hex='#ff0000', end_hex='#0000ff', mid_hex='#ffffff', color_transform=None
):
    """
    For a particular Bokeh model and accompanying keyword arguents,
    automatically set color and alpha values.
    
    """
        
    if 'color' in kwargs.keys():
        color = kwargs.pop('color')
        for v in bokeh_model.dataspecs():
            if 'color' in v:
                kwargs[v] = color

    color_keys = [key for key in bokeh_model.dataspecs() if ('color' in key) and (key in kwargs.keys())]

    new_fields = dict()
    for key in color_keys:
        color_val = kwargs[key]
        if color_val is None:
            continue
        if color_val is None:
            continue
        if isinstance(color_val, str):
            if check_color(color_val):
                continue
            else:
                color_arr = source_df[color_val].tolist()
                in_datasource = True
        else:
            color_arr = color_val
            in_datasource = False

        if not all(check_color(c) for c in color_arr):
            color_new = assign_colors(
                color_arr, start_hex, end_hex, mid_hex, color_transform, categorical_palette
            )
            if in_datasource:
                new_val = '{}_autocolor'.format(color_val)
                new_fields[new_val] = color_new
                kwargs[key] = new_val
            else:
                kwargs[key] = color_new

    if 'alpha' in kwargs.keys():
        alpha = kwargs.pop('alpha')
        for v in bokeh_model.dataspecs():
            if 'alpha' in v:
                kwargs[v] = alpha
                    
    return kwargs, new_fields
