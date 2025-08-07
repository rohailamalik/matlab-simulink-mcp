function varargout = imread(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('imread', varargin{:});
end