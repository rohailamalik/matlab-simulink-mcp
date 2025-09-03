% Define x values
x = linspace(0, 2*pi, 1000);

% Compute sine and cosine
y_sin = sin(x);
y_cos = cos(x);

% Plot sine
figure;
plot(x, y_sin);
title('Sine Function');
xlabel('x');
ylabel('sin(x)');

% Plot cosine
figure;
plot(x, y_cos);
title('Cosine Function');
xlabel('x');
ylabel('cos(x)');

% Compute and print averages
avg_sin = mean(y_sin);
avg_cos = mean(y_cos);

fprintf('Average of sine values: %.4f\n', avg_sin);
fprintf('Average of cosine values: %.4f\n', avg_cos);
