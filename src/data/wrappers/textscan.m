function varargout = textscan(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('textscan', varargin{:});
end