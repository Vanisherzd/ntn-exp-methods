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
