"""Make upstream telemanom's 2018 Keras import paths resolve on modern Keras.

keras.layers.recurrent and keras.layers.core were removed. Upstream modeling.py imports LSTM from
the former and Dense/Activation/Dropout from the latter. Registering alias modules lets upstream
code run VERBATIM instead of being ported, which is the more faithful arm.
"""
import sys, types
try:
    import keras
    from keras import layers as _L
except Exception:
    keras = None
if keras is not None:
    for name, syms in (("keras.layers.recurrent", ["LSTM"]),
                       ("keras.layers.core", ["Dense", "Activation", "Dropout"])):
        if name not in sys.modules:
            m = types.ModuleType(name)
            for s in syms:
                setattr(m, s, getattr(_L, s))
            sys.modules[name] = m
            setattr(sys.modules["keras.layers"], name.rsplit(".", 1)[1], m)


# ---------------------------------------------------------------- numpy bridge
# Upstream pins numpy==1.17.4. In errors.py:407-418 `i_to_remove` is created as np.array([]),
# which is float64, and stays float64 after np.append; numpy 1.17 accepted a float index array
# for np.delete with a deprecation warning, numpy 2 raises IndexError. The values are always
# integral positions, so casting is SEMANTICALLY IDENTICAL -- this changes no behaviour and no
# threshold, it only lets upstream's own pruning code run on a modern numpy.
#
# Done here rather than by editing the clone so that upstream source stays byte-identical and the
# per-file sha256 hashes recorded in run_manifest.json still verify. The cast is applied only when
# the index array is floating AND every value is integral; anything else passes straight through,
# so a genuinely fractional index would still raise rather than be silently rounded.
import numpy as _np

_delete = _np.delete


def _delete_intcast(arr, obj, axis=None):
    if isinstance(obj, _np.ndarray) and obj.dtype.kind == "f":
        if obj.size == 0:
            obj = obj.astype(_np.intp)
        elif _np.all(obj == _np.rint(obj)):
            obj = obj.astype(_np.intp)
    return _delete(arr, obj, axis=axis)


_np.delete = _delete_intcast
