function F_drag = calculate_drag_force(velocity, drag_coefficient, frontal_area, air_density)
    % CALCULATE_DRAG_FORCE - Calculates aerodynamic drag force on an object
    %
    % Syntax: F_drag = calculate_drag_force(velocity, drag_coefficient, frontal_area, air_density)
    %
    % Inputs:
    %   velocity - Velocity of the object (m/s)
    %   drag_coefficient - Drag coefficient (dimensionless, typically 0.2-1.5)
    %   frontal_area - Frontal area of the object (m^2)
    %   air_density - Density of air (kg/m^3, typically 1.225 at sea level)
    %
    % Outputs:
    %   F_drag - Drag force (N)
    %
    % Formula: F_drag = 0.5 * air_density * velocity^2 * drag_coefficient * frontal_area
    %
    % Example:
    %   F_drag = calculate_drag_force(30, 0.3, 2.5, 1.225)
    
    % Input validation
    if nargin < 4
        error('Not enough input arguments. Required: velocity, drag_coefficient, frontal_area, air_density');
    end
    
    if any([velocity, drag_coefficient, frontal_area, air_density] < 0)
        error('All input values must be non-negative');
    end
    
    % Calculate drag force using the standard aerodynamic drag equation
    F_drag = 0.5 * air_density * velocity^2 * drag_coefficient * frontal_area;
    
    % Display results
    fprintf('Drag Force Calculation:\n');
    fprintf('  Velocity: %.2f m/s\n', velocity);
    fprintf('  Drag Coefficient: %.3f\n', drag_coefficient);
    fprintf('  Frontal Area: %.2f m^2\n', frontal_area);
    fprintf('  Air Density: %.3f kg/m^3\n', air_density);
    fprintf('  Drag Force: %.2f N\n', F_drag);
    
end