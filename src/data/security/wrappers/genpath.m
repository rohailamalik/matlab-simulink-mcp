function varargout = genpath(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('genpath', varargin{:});
end