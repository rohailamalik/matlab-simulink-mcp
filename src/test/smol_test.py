from core.server import start_server
import math
import numpy as np
from typing import Any, Dict, List 
from core.tools import open_matlab_file, open_simulink_file, save_matlab_code, get_variables, get_workspace_summary, search_library, run_matlab_code


import matlab.engine
start_server()
from core.state import server_state, get_engine


from utils.converters import fetch, batch_fetch, convert_supported, convert_non_supported, flatten_struct_array, reshape_recursive      

eng = server_state.eng

import IPython; IPython.embed()

#huh = batch_fetch(eng, ["str"], convert=False)
#print(huh)


code = """

x = linspace(1, 10, 1000);
y = sin(x) + cos(x);

z = zeros(size(x));
for i = 2:length(x)
    z(i) = z(i-1) + y(i);
end

disp('x:');
disp(x);
disp('y:');
disp(y);
disp('z:');
disp(z);



"""

result = eng.evalc(code)
print(result)