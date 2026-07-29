function WriteOwiDelft3D(D,filename)

%==========================================================================
% Write Delft3D meteorological forcing files
%
% Outputs:
%   *.amu  - x wind
%   *.amv  - y wind
%   *.ampr - air pressure
%==========================================================================

%% Check required fields

flds = {'time','iLat','iLong','DX','DY','SWLat','SWLon',...
        'XGrid','YGrid','Pre','WinU','WinV'};

if ~isfield(D,'Basin')
    error('OwiStruct must have Basin grid defined.')
elseif ~all(isfield(D.Basin,flds))
    error('Input OwiStruct.Basin is missing required fields.')
end

%% Output files

BasinWinUFile = [filename '_Delft3D.amu'];
BasinWinVFile = [filename '_Delft3D.amv'];
BasinPreFile  = [filename '_Delft3D.ampr'];

fidu = fopen(BasinWinUFile,'w');
fidv = fopen(BasinWinVFile,'w');
fidp = fopen(BasinPreFile ,'w');

%% Header

header = {...
'### START OF HEADER';
'### This file is created by Deltares';
'### Additional comments';
'FileVersion = 1.03';
'filetype = meteo_on_equidistant_grid';
'NODATA_value = -9999.0';
['n_cols = ' num2str(D.Basin.iLong(1))];
['n_rows = ' num2str(D.Basin.iLat(1))];
'grid_unit = m';
['x_llcenter = ' num2str(D.Basin.SWLon(1))];
['y_llcenter = ' num2str(D.Basin.SWLat(1))];
['dx = ' num2str(D.Basin.DX(1))];
['dy = ' num2str(D.Basin.DY(1))];
'n_quantity = 1'};

for i = 1:numel(header)
    fprintf(fidu,'%s\n',header{i});
    fprintf(fidv,'%s\n',header{i});
    fprintf(fidp,'%s\n',header{i});
end

%% Variable definitions

fprintf(fidu,'quantity1 = x_wind\n');
fprintf(fidu,'unit1 = m s-1\n');
fprintf(fidu,'### END OF HEADER\n');

fprintf(fidv,'quantity1 = y_wind\n');
fprintf(fidv,'unit1 = m s-1\n');
fprintf(fidv,'### END OF HEADER\n');

fprintf(fidp,'quantity1 = air_pressure\n');
fprintf(fidp,'unit1 = mbar\n');
fprintf(fidp,'### END OF HEADER\n');

%% Time records

headerT2 = ' hours since 2017-01-01 00:00:00 +00:00';

for j = 1:length(D.Basin.time)

    fprintf(fidu,'TIME = %d%s\n',j-1,headerT2);
    fprintf(fidv,'TIME = %d%s\n',j-1,headerT2);
    fprintf(fidp,'TIME = %d%s\n',j-1,headerT2);

    outU = D.Basin.WinU{j};
    outV = D.Basin.WinV{j};
    outP = D.Basin.Pre{j};

    for k = 1:D.Basin.iLat(1)

        fprintf(fidu,'%12.4f',outU(k,:).');
        fprintf(fidu,'\n');

        fprintf(fidv,'%12.4f',outV(k,:).');
        fprintf(fidv,'\n');

        fprintf(fidp,'%12.4f',outP(k,:).');
        fprintf(fidp,'\n');

    end

end

%% Close files

fclose(fidu);
fclose(fidv);
fclose(fidp);

end