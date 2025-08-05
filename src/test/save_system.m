function varargout = save_system(varargin)
    check_args('write', varargin);  % or 'run', depending on your policy
    [varargout{1:nargout}] = builtin('save_system', varargin{:});
end