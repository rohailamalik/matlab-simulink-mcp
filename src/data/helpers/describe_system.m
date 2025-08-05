function system_data = describe_system(system_path)

% This function returns the information about a system layout as a JSON. 
% It's still problematic with Simscape because some blocks such as
% SolverConfiguration and PS-Simulink Convertor are defined internally as
% SubSystems instead of Simscape blocks.

    blocks = find_system(system_path, 'SearchDepth', 1, 'Type', 'Block');

    elements = {};
    connections = {};

    for i = 1:length(blocks)

        blk = blocks{i};
        blk_source = get_param(blk, 'ReferenceBlock');

        element = struct();
        element.Name = get_param(blk, 'Name');
        element.Type = get_param(blk, 'BlockType');
        
        if blk_source ~= ""
            element.Source = blk_source;
        end 

        if ~strcmp(element.Type, "SimscapeBlock") && ~strcmp(element.Type, "SubSystem")
            % It's a built-in simulink block
            if blk_source ~= ""
                element.Source = ['built-in/' element.Type];
            end 
            element.Type = "Block";
                     
        end

        [inports, outports, simscapeports, connects] = get_ports_connections(blk, element.Name, element.Type);
        
        if ~isempty(inports), element.Inports = inports; end
        if ~isempty(outports), element.Outports = outports; end
        if ~isempty(simscapeports), element.SimscapePorts = simscapeports; end
        if ~isempty(connects), connections = [connections, connects]; end

        elements{end+1} = element;

    end

    system = struct();
    system.Elements = elements;
    system.Connections = connections; 

    system_data = jsonencode(system);
    %system_data = system;

end
