function g_deceleration = calculate_deceleration(speed, mass, drag_coeff, frontal_area, air_density)
    % Function to compute deceleration in terms of g due to drag force
    %
    % Inputs:
    %   speed          - Velocity of the car (m/s)
    %   mass           - Mass of the car (kg)
    %   drag_coeff     - Drag coefficient (dimensionless)
    %   frontal_area   - Frontal area of the car (m^2)
    %   air_density    - Density of air (kg/m^3)
    %
    % Output:
    %   g_deceleration - Deceleration in terms of g

    % Constants
    g = 9.81; % Acceleration due to gravity (m/s^2)

    % Drag force formula: F_drag = 0.5 * drag_coeff * air_density * frontal_area * speed^2
    F_drag = 0.5 * drag_coeff * air_density * frontal_area * speed^2;

    % Acceleration due to drag: a = F_drag / mass
    acceleration = F_drag / mass;

    % Deceleration in terms of g: g_deceleration = acceleration / g
    g_deceleration = acceleration / g;
end