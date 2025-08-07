function varargout = xlsread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('xlsread', varargin{:});
end