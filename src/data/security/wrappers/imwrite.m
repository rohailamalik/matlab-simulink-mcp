function varargout = imwrite(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('imwrite', varargin{:});
end