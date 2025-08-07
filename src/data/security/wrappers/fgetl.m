function varargout = fgetl(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('fgetl', varargin{:});
end