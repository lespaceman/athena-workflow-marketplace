"""Evaluator package.

Importing this package walks every submodule so that any ``@register``-decorated
``Evaluator`` subclass populates ``evals.evaluators.base.EVALUATORS`` as a side
effect of import. This keeps ``EVALUATORS`` populated without an explicit
import list that would have to be hand-maintained.
"""

from __future__ import annotations

import importlib
import pkgutil

from evals.evaluators.base import EVALUATORS, EvalContext, EvalResult, Evaluator, register

__all__ = ["EVALUATORS", "EvalContext", "EvalResult", "Evaluator", "register"]


def _autoload_submodules() -> None:
    for module_info in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
        # Skip the base module (already imported above) to avoid noisy reimport.
        if module_info.name.endswith(".base"):
            continue
        importlib.import_module(module_info.name)


_autoload_submodules()
