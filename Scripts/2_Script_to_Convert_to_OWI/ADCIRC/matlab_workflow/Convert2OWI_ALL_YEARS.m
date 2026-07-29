clear; clc;

% ========================================================================
% Convert ERA5 NetCDF files to ADCIRC OWI meteorological forcing files
%
% This script:
%   1. Reads ERA5 hourly meteorological data from NetCDF files
%   2. Extracts:
%        - Mean Sea Level Pressure (msl)
%        - 10 m U-wind component (u10)
%        - 10 m V-wind component (v10)
%   3. Reformats the ERA5 grids into ADCIRC OWI format
%   4. Creates yearly OWI pressure (*.pre) and wind (*.win) files
%
% Requirements:
%   - ERA5 NetCDF files (era5_YYYY.nc)
%   - WriteOwi.m
%
% Output:
%   era5_YYYY_formatOWI_Basin.pre
%   era5_YYYY_formatOWI_Basin.win
%
% Notes:
%   ERA5 stores variables as:
%       longitude x latitude x time
%
%   ADCIRC OWI expects:
%       latitude x longitude x time
%
%   Therefore the data must be permuted and reoriented before writing.
%
% ========================================================================

% Define years you want to process
% Example:
%   1979:2019  -> full record
%   1999:2019  -> subset for testing
years = 1999:2019;   % you can change this to 1979:2019

for yr = years

    % --------------------------------------------------------------------
    % Construct ERA5 NetCDF file name for the current year
    % Example:
    %   era5_1979.nc
    % --------------------------------------------------------------------
    ncName = sprintf('era5_%d.nc', yr);

    fprintf('=== Processing %s ===\n', ncName);

    % --------------------------------------------------------------------
    % Read time variable
    %
    % ERA5 valid_time is stored as:
    %   seconds since 1970-01-01 00:00:00 UTC
    %
    % Convert to MATLAB datenum format because WriteOwi expects MATLAB
    % serial date numbers.
    % --------------------------------------------------------------------
    time = ncread(ncName, "valid_time");
    time = datenum(datetime(1970,1,1) + seconds(time));

    % --------------------------------------------------------------------
    % Read coordinate variables
    %
    % latitude  -> degrees north
    % longitude -> degrees east
    % --------------------------------------------------------------------
    lat = ncread(ncName, "latitude");
    lon = ncread(ncName, "longitude");

    % --------------------------------------------------------------------
    % Read meteorological variables
    %
    % msl  = Mean Sea Level Pressure (Pa)
    % u10  = East-West wind component at 10 m (m/s)
    % v10  = North-South wind component at 10 m (m/s)
    %
    % ADCIRC OWI pressure files use millibars (mb), so convert:
    %
    %   1 mb = 100 Pa
    %
    % Therefore:
    %   Pa * 0.01 = mb
    % --------------------------------------------------------------------
    msl = ncread(ncName, "msl") * 0.01; % Pa → mb
    u10 = ncread(ncName, "u10");
    v10 = ncread(ncName, "v10");

    % --------------------------------------------------------------------
    % Reorient ERA5 arrays
    %
    % ERA5 dimensions:
    %   longitude x latitude x time
    %
    % OWI expects:
    %   latitude x longitude x time
    %
    % Swap longitude and latitude dimensions.
    % --------------------------------------------------------------------
    msl = permute(msl, [2 1 3]);
    u10 = permute(u10, [2 1 3]);
    v10 = permute(v10, [2 1 3]);

    % --------------------------------------------------------------------
    % Flip latitude dimension
    %
    % ERA5 latitude is commonly stored:
    %   North -> South
    %
    % OWI expects the first row to correspond to the northernmost latitude.
    %
    % Flip the arrays vertically to ensure proper orientation.
    % --------------------------------------------------------------------
    msl = flipud(msl);
    u10 = flipud(u10);
    v10 = flipud(v10);

    % --------------------------------------------------------------------
    % Initialize OWI structure
    %
    % Basin grid information is required by WriteOwi.m
    % --------------------------------------------------------------------
    owi.Basin = [];

    % Time vector
    owi.Basin.time  = time';

    % Number of latitude points
    owi.Basin.iLat  = length(lat) * ones(1,length(time));

    % Number of longitude points
    owi.Basin.iLong = length(lon) * ones(1,length(time));

    % Grid spacing in longitude direction
    owi.Basin.DX    = abs(lon(1) - lon(2)) * ones(1,length(time));

    % Grid spacing in latitude direction
    owi.Basin.DY    = abs(lat(1) - lat(2)) * ones(1,length(time));

    % Southwest corner latitude
    owi.Basin.SWLat = lat(end) * ones(1,length(time));

    % Southwest corner longitude
    owi.Basin.SWLon = lon(1) * ones(1,length(time));

    % Store coordinate vectors for each timestep
    [owi.Basin.XGrid{1:length(time)}] = deal(lon');
    [owi.Basin.YGrid{1:length(time)}] = deal(flip(lat));

    % --------------------------------------------------------------------
    % Populate OWI fields
    %
    % For each timestep:
    %   Pre  = pressure field
    %   WinU = east-west wind component
    %   WinV = north-south wind component
    % --------------------------------------------------------------------
    for i = 1:length(time)
        owi.Basin.Pre{i}  = msl(:,:,i);
        owi.Basin.WinU{i} = u10(:,:,i);
        owi.Basin.WinV{i} = v10(:,:,i);
    end

    % --------------------------------------------------------------------
    % No nested regional grid is used in this workflow.
    % Basin-only forcing is generated.
    % --------------------------------------------------------------------
    owi.Region = [];

    % --------------------------------------------------------------------
    % Write OWI files
    %
    % Example output:
    %
    %   era5_1979_formatOWI_Basin.pre
    %   era5_1979_formatOWI_Basin.win
    %
    % --------------------------------------------------------------------
    outName = sprintf('era5_%d_formatOWI', yr);
    WriteOwi(owi, outName);

    % --------------------------------------------------------------------
    % Clear large variables before moving to next year
    %
    % This helps reduce MATLAB memory usage when processing
    % multi-decadal datasets.
    % --------------------------------------------------------------------
    clear owi time lat lon msl u10 v10

end