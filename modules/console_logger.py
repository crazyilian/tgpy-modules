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
        with open("/dev/stdout", "w") as f:
            tm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text = sep.join(map(str, args))
            f.write(f"[{tm}] {self.prefix}{text}{end}")

    def input(self, str):
        self.print(str, end='')
        return input()


__all__ = ['ConsoleLogger']
