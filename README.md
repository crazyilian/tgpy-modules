# TGPy modules by crazyilian

Modules pack for [TGPy](https://tgpy.tmat.me/).

## Installation

Clone repo and copy or create symlink to all modules. For example:

```bash
git clone https://github.com/crazyilian/tgpy-modules.git
ln -s tgpy-modules.git/modules/* ~/.config/tgpy/modules/*
```

Install requirements in your TGPy environment. For example

```bash
~/tgpy-venv/bin/python3 -m pip install -r tgpy-modules.git/requirements.txt
```

The first time you run TGPy with these modules, you may be asked to enter some data (e.g. bot token for `pet_bot.py`).

## Updating

Just `git pull` cloned repo. You can do this in terminal or inside telegram:

```bash
.sh
cd path/to/tgpy-modules.git
git pull
```

After that you need to restart TGPy. You can do this in terminal or inside telegram:

```python
restart()
```
