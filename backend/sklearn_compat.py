"""
Scikit-Learn Backward & Forward Compatibility Layer
Ensures serialized ColumnTransformer and Pipeline artifacts from scikit-learn 1.8.x
can be deserialized seamlessly across all scikit-learn versions (1.6.x - 1.9.x+)
by shimming internal attributes such as _RemainderColsList if missing.
"""

from collections import UserList
import logging

logger = logging.getLogger("aquora.compat")


def apply_sklearn_compat():
    """Ensure _RemainderColsList exists on sklearn.compose._column_transformer."""
    try:
        import sklearn.compose._column_transformer as ct

        if not hasattr(ct, "_RemainderColsList"):
            class _RemainderColsList(UserList):
                """Compatibility fallback for deserializing ColumnTransformers saved in scikit-learn <= 1.8."""

                def __init__(
                    self,
                    columns=(),
                    *,
                    future_dtype=None,
                    warning_was_emitted=False,
                    warning_enabled=True,
                ):
                    super().__init__(columns)
                    self.future_dtype = future_dtype
                    self.warning_was_emitted = warning_was_emitted
                    self.warning_enabled = warning_enabled

                def __getitem__(self, index):
                    return super().__getitem__(index)

            ct._RemainderColsList = _RemainderColsList
            logger.info("Applied compatibility shim for sklearn.compose._column_transformer._RemainderColsList")
    except Exception as e:
        logger.debug(f"Notice: sklearn compat check: {e}")


# Apply immediately upon import
apply_sklearn_compat()
