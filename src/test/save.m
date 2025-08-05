function save(varargin)
    check_args('write', varargin);
    builtin('save', varargin{:});
end