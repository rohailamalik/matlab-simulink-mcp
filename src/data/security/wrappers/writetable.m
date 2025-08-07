function varargout = writetable(varargin)
    check_args('write', varargin);
    [varargout{1:nargout}] = builtin('writetable', varargin{:});
end