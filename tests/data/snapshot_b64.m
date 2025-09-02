function snapshot_b64(system, dpi)

if nargin < 2
    dpi = '150'; 
end

path = "-s" + system;
quality = "-r" + dpi;
file = "snapshot.png";

print(path, "-dpng", quality, file);


%fid = fopen(file, 'rb');
%bytes = fread(fid, '*uint8')';
% fclose(fid);

%b64 = matlab.net.base64encode(bytes);
%delete(file);
end