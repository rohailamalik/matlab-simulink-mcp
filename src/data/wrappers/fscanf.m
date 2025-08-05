function varargout = fscanf(varargin)
    check_args('read', varargin);
    [varargout{1:nargout}] = builtin('fscanf', varargin{:});
end