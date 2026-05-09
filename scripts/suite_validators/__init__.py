from .common import SuiteContext, run_assertions
from .intent import validate_intent
from .playwright import validate_playwright
from .robot import validate_robot

SUITES = {
    "playwright": validate_playwright,
    "robot": validate_robot,
    "intent": validate_intent,
}

__all__ = ["SUITES", "SuiteContext", "run_assertions", "validate_playwright", "validate_robot", "validate_intent"]
