% Delete disconnected blocks
try
    % Blocks to delete
    delete_block('elecmechsim/Lin Motor Sys');
    delete_block('elecmechsim/DC Motor');
    delete_block('elecmechsim/Vehicle');

catch ME
    disp(ME.message);
end