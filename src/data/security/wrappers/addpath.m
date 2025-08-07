function varargout = addpath(varargin)
    check_args('ban', varargin);
    [varargout{1:nargout}] = builtin('addpath', varargin{:});
end