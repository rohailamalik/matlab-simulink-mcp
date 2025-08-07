function varargout = uiputfile(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('uiputfile', varargin{:});
end