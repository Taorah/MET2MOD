import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind', 'mean_sea_level_pressure',
        ],
        'year': '2020',
        'month': '01',
        'day': '01',
        'time': '00:00',
        'format': 'netcdf',
        'area': [
            50, -99, 5,
            -59,
        ],
    },
    'era5_20200101.nc')

