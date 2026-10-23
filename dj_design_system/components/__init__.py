"""Component base classes and the package's built-in components.

The base classes live in :mod:`dj_design_system.components.base` and are
re-exported here, so ``from dj_design_system.components import TagComponent``
keeps working. Built-in components live in subpackages of this package.
"""

from dj_design_system.components.base import (
    BaseComponent,
    BlockComponent,
    TagComponent,
)


__all__ = ["BaseComponent", "BlockComponent", "TagComponent"]
