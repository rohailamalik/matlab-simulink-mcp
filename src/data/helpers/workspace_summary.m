function summary = workspace_summary()

who = rmfield(whos(), setdiff(fieldnames(whos()), {'name', 'size', 'class'}));
summary = jsonencode(who);
