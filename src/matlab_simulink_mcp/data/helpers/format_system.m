function result = format_system(system_path, main_system, arrange)

load_system(main_system)

if arrange
    Simulink.BlockDiagram.arrangeSystem(system_path);
end 

hLines = find_system(system_path, 'SearchDepth', 1, 'FindAll', 'on', 'Type', 'Line', 'Connected', 'off');
delete_line(hLines);
result = "Success";


