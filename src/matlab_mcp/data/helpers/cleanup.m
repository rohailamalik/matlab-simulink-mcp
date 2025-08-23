function result = cleanup(target, mode)
% CLEANUP  Remove dangling or orphaned blocks/lines from a Simulink system.

% Args:
%   system : name/handle of the model or subsystem
%   target : 'block' | 'line' | 'both'
%   mode   : 'dangling' (partially unconnected) 
%            'orphaned' (fully unconnected)
%
% Returns:
%   result : struct with fields:
%              .deletedBlocks
%              .deletedLines

result = struct('deletedBlocks',0,'deletedLines',0);
system = gcs();

% Lines
if strcmpi(target,'line') || strcmpi(target,'both')
    hLines = find_system(system,'FindAll','on','Type','Line');
    for h = reshape(hLines,1,[])
        src = get_param(h,'SrcPortHandle');
        dst = get_param(h,'DstPortHandle');
        switch lower(mode)
            case 'orphaned' % fully unconnected
                if src == -1 && all(dst == -1)
                    delete_line(h);
                    result.deletedLines = result.deletedLines + 1;
                end
            case 'dangling' % at least one end unconnected
                if src == -1 || all(dst == -1)
                    delete_line(h);
                    result.deletedLines = result.deletedLines + 1;
                end
        end
    end
end

% Blocks
if strcmpi(target,'block') || strcmpi(target,'both')
    hBlocks = find_system(system,'SearchDepth',1,'Type','Block');
    for k = 1:numel(hBlocks)
        ports = get_param(hBlocks{k},'PortConnectivity');
        isConnected = arrayfun(@(p) ~isempty(p.SrcBlock) || ~isempty(p.DstBlock), ports);
        if isempty(isConnected)
            isConnected = false; % e.g. blocks with no ports
        end
        switch lower(mode)
            case 'orphaned'
                if ~any(isConnected)
                    delete_block(hBlocks{k});
                    result.deletedBlocks = result.deletedBlocks + 1;
                end
            case 'dangling'
                if ~all(isConnected)
                    delete_block(hBlocks{k});
                    result.deletedBlocks = result.deletedBlocks + 1;
                end
        end
    end
end

