"""
    description: wrapper of tgpy.api.config for modules (default config, required values
      input)
    name: config_loader
    version: 0.0.0
"""
import tgpy.api
import logging


class ModuleConfig:
    module_name = None
    logger = None

    def __init__(self, module_name, required_keys=None, map_required_keys=None, default_dict=None):
        if required_keys is None:
            required_keys = []
        if map_required_keys is None:
            map_required_keys = [str] * len(required_keys)
        if default_dict is None:
            default_dict = {}
        self.module_name = module_name
        self.logger = logging.getLogger(f'config_loader.{module_name}')

        config = self.get_config()

        correct_config = True
        for key, func in zip(required_keys, map_required_keys):
            if key not in config:
                if correct_config:
                    correct_config = False
                    pretty_name = module_name.replace("_", " ").title()
                    self.logger.info(f'"{pretty_name}" module configuration is incomplete.')
                self.logger.info(f'│ Please enter "{key}":')
                config[key] = func(input())
        if not correct_config:
            self.logger.info("| Configuration completed.")

        for key in default_dict:
            if key not in config:
                config[key] = default_dict[key]
        self.save(config)

    def save(self, config=None):
        if config is None:
            tgpy.api.config.save()
        else:
            tgpy.api.config.set(f'config_loader.{self.module_name}', config)

    def get_config(self):
        return tgpy.api.config.get(f'config_loader.{self.module_name}', {})

    def __getitem__(self, item):
        return tgpy.api.config.get(f'config_loader.{self.module_name}.{item}')

    def __setitem__(self, key, value):
        return tgpy.api.config.set(f'config_loader.{self.module_name}.{key}', value)

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        if key in dir(self):
            super(ModuleConfig, self).__setattr__(key, value)
        else:
            self[key] = value
