"""Constant values and defaults used in multiple modules."""
import enum


class State(enum.Enum):
    CREATED = 'CREATED'
    FUNDING = 'FUNDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELED = 'CANCELED'


states = [state.value for state in State]
