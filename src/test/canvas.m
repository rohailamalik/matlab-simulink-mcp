% Open the model if not already open
load_system('elecmechsim');

% List of blocks to remove based on new analysis
blocksToRemove = { ...
    'elecmechsim/DiscreteIntegrator2', ...
    'elecmechsim/nooo', ...
    'elecmechsim/Lin Motor Sys' ...
};

% Iterate and remove the blocks
for i = 1:length(blocksToRemove)
    if bdIsLoaded('elecmechsim') && ishandle(get_param(blocksToRemove{i}, 'Handle'))
        delete_block(blocksToRemove{i});
    end
end

% Save the modified model without closing
save_system('elecmechsim');