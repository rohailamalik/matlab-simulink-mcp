function varargout = openfig(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('openfig', varargin{:});
end