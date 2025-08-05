function varargout = csvwrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('csvwrite', varargin{:});
end