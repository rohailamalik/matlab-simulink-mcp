function delete(varargin)
    check_args('delete', varargin);
    builtin('delete', varargin{:});
end