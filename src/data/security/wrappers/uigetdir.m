function varargout = uigetdir(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('uigetdir', varargin{:});
end