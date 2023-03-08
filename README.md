# TGPy modules made by crazyilian

*made or edited

Some modules made for [TGpy](https://github.com/tm-a-t/TGPy).

## Installation


### Nya

To install `nya` module manager, send the following message to any chat (it can be "Saved Messages" either):
```python
import subprocess, sys; subprocess.run([sys.executable, "-m", "pip", "install", "gists.py"], check=True); import gists
source = "https://gist.github.com/miralushch/b43ce0642f89814981f341308ba9dac9"
code = (await gists.Client().get_gist(source)).files[0].content
nya = (await tgpy.api.tgpy_eval(code + '\nnya')).result[-1]
nya.install(source, code)
```


### Modules from this repo

To add all the modules to `nya` registry, send the following message to any chat:

```python
source = "https://raw.githubusercontent.com/crazyilian/tgpy-modules/main/modules/github_registry.py"
code = await (await nya._Nya__aiohttp_session.get(source)).text()
gh_reg = (await __import__("tgpy.api").api.tgpy_eval(code + "\ngh_reg")).result[-1]
nya.import_src_list(await gh_reg.get_sources('crazyilian/tgpy-modules/tree/main/modules'))
```

After that to install module `{name}.py`, send message:
```python
nya.reg_install("{name}")
```