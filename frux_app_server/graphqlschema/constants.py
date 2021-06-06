"""Constant values and defaults used in multiple modules."""
import enum


class Stage(enum.Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    ALMOST_DONE = 'ALMOST_DONE'
    COMPLETE = 'COMPLETE'


class State(enum.Enum):
    CREATED = 'CREATED'
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'
    CANCELLED = 'CANCELLED'
    COMPLETE = 'COMPLETE'
    EXPIRED = 'EXPIRED'


stages = [stage.value for stage in Stage]
states = [state.value for state in State]
