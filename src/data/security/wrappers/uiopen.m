function varargout = uiopen(varargin)
    check_args('ban', varargin);
    [varargout{1:nargout}] = builtin('uiopen', varargin{:});
end