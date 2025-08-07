function varargout = fprintf(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('fprintf', varargin{:});
end