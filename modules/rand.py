"""
    description: generate random from expanded string (e.g. rand("{1..100}") -> random
      int from 1 to 100)
    name: rand
    needs:
      dot: 0.1.0
      expand: 0.0.0
    version: 0.0.0
"""
import random


@dot('rand')
def rand(s=''):
    return random.choice(expand(s))
