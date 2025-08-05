function varargout = csvread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('csvread', varargin{:});
end