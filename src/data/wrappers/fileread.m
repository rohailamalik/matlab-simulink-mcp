function varargout = fileread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('fileread', varargin{:});
end