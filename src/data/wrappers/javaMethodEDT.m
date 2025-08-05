function varargout = javaMethodEDT(varargin)
    check_args('system', varargin);
    [varargout{1:nargout}] = builtin('javaMethodEDT', varargin{:});
end