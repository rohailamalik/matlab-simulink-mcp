function varargout = writematrix(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('writematrix', varargin{:});
end