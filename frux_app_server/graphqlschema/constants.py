"""Constant values and defaults used in multiple modules."""
import enum


class State(enum.Enum):
    CREATED = 'CREATED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETE = 'COMPLETE'


states = [state.value for state in State]
