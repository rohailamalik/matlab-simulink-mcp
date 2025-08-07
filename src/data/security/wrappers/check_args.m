function check_args(mode, args)
    for i = 1:numel(args)
        arg = args{i};
        if ischar(arg) || isstring(arg)
            assert_safe_path(char(arg), mode);
        end
    end
end