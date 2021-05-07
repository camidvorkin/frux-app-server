"""Constant values and defaults used in multiple modules."""
import enum


class Category(enum.Enum):
    SPORTS = 'SPORTS'
    ART = 'ART'
    MUSIC = 'MUSIC'
    OTHERS = 'OTHERS'


class State(enum.Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    ALMOST_DONE = 'ALMOST_DONE'
    COMPLETE = 'COMPLETE'


categories = [category.value for category in Category]
states = [state.value for state in State]
