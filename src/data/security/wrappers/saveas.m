function varargout = saveas(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('saveas', varargin{:});
end