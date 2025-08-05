function varargout = xlswrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('xlswrite', varargin{:});
end