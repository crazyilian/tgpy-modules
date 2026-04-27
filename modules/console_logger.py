"""
    name: console_logger
    once: false
    origin: tgpy://module/console_logger
    priority: 0
"""
import datetime


class ConsoleLogger:
    def __init__(self, prefix=''):
        self.prefix = prefix
        self.print("logger initialized")

    def print(self, *args, sep=' ', end='\n'):
        tm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = sep.join(map(str, args))
        print(f"[{tm}] {self.prefix}{text}{end}", end='')

    def input(self, str):
        self.print(str, end='')
        return input()


__all__ = ['ConsoleLogger']
