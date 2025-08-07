function varargout = fileparts(varargin)
    check_args('path', varargin);
    [varargout{1:nargout}] = builtin('fileparts', varargin{:});
end