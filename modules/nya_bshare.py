"""
    description: better share for Nya - help(nya.bshare)
    name: nya_bshare
    needs:
      nya: 0.25.1
    version: 0.3.0
"""
from telethon.errors.rpcerrorlist import MessageTooLongError
import tgpy.api
import json
from copy import deepcopy


def fix_share_parameters(params, codec=None, by_file=None, minify=None):
    if isinstance(params, str) or isinstance(params, dict) or isinstance(params, Codec):
        params = [params]
    result_params = []
    for param in params:
        if isinstance(param, str):
            param = {'codec': Codec(value=param)}
        elif isinstance(param, Codec):
            param = {'codec': param}
        elif param is None:
            param = {}
        param = {
            'codec': param.get('codec', codec or Codec(value=tgpy.api.config.get('share.codec'))),
            'by_file': param.get('by_file', by_file or tgpy.api.config.get('share.by_file')),
            'minify': param.get('minify', minify or tgpy.api.config.get('share.minify')),
        }
        result_params.append(param)
    return result_params


class NyaBetterShare:
    def __init__(self, nya):
        self.nya = nya
        if tgpy.api.config.get('bshare.params') is None:
            self.set_default_params([{}, {'codec': Codec.NONE, 'by_file': True, 'minify': False}])
        if tgpy.api.config.get('bshare.show_params'):
            self.set_show_params(False)

    async def __call__(self, name: str, codec: Codec | None = None, by_file: bool | None = None,
                       minify: bool | None = None,
                       params: list[dict] = None):
        """
            Share installed module {name}.
            Try to share module with parameters according to {params} in giving order.
            {params} is list of dicts {'codec': Codec|str|None, 'by_file': bool|None, 'minify': bool|None}.
            If params is None, use default bshare parameters from config.
            If some value in parameters is not set, use values from arguments.
            If values from arguments is None, use default values from nya share config.
            Initial config params are [{}, {'codec': Codec.NONE, 'by_file': True, 'minify': False}]
            (try to send with the default share config, and if that fails, send the source code by file).
        """
        if params is None:
            params = self.get_default_params()
        params = fix_share_parameters(params, codec, by_file, minify)
        for param in params:
            try:
                codec_, by_file_, minify_ = [param[key] for key in ['codec', 'by_file', 'minify']]
                await self.nya.share(name, codec=codec_, by_file=by_file_, minify=minify_)
                if self.get_show_params():
                    print(f'Share parameters:\ncodec = "{codec_.value}"\nby_file = {by_file_}\nminify = {minify_}')
                else:
                    print('Done')
                return
            except MessageTooLongError:
                continue
            except FileNotFoundError:
                print(f"No module {name} found")
                return
        print(f"Module {name} is too big to send it this way")

    async def file(self, name, codec=None, minify=None):
        """Shortcut for nya.share({name}, by_file=True)"""
        await self(name, codec=codec, by_file=True, minify=minify, params=[{}])

    async def text(self, name, codec=None, minify=None):
        """Shortcut for nya.share({name}, by_file=False)"""
        await self(name, codec=codec, by_file=False, minify=minify, params=[{}])

    @staticmethod
    def set_default_params(params: list[dict]):
        """
            Set the default parameters for bshare.
            {params} is list of dicts {'codec': Codec|str|None, 'by_file': bool|None, 'minify': bool|None}.
        """
        json_params = []
        for param in fix_share_parameters(params):
            json_params.append(deepcopy(param))
            if isinstance(param, Codec):
                json_params[-1] = param.value
            elif isinstance(param, dict) and 'codec' in param and isinstance(param['codec'], Codec):
                json_params[-1]['codec'] = param['codec'].value
        json.dumps(json_params)
        tgpy.api.config.set('bshare.params', json_params)

    @staticmethod
    def get_default_params():
        """Get the default parameters for bshare."""
        json_params = tgpy.api.config.get('bshare.params')
        params = []
        for param in json_params:
            params.append(deepcopy(param))
            if isinstance(param, str):
                params[-1] = Codec(value=param)
            elif isinstance(param, dict) and 'codec' in param:
                params[-1]['codec'] = Codec(value=param['codec'])
        return params

    @staticmethod
    def set_show_params(show: bool):
        """Set config flag, show share parameters on sharing or not"""
        json.dumps(show)
        tgpy.api.config.set('bshare.show_params', show)

    @staticmethod
    def get_show_params():
        """Get config flag, show share parameters on sharing or not"""
        return tgpy.api.config.get('bshare.show_params')


nya.bshare = NyaBetterShare(nya)

__all__ = []
