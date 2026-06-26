# Analyzer Validation Note

This note checks the `rx_samples_to_file` fallback parsing path.

- Fallback capture command uses `--type float`.
- The parser reads interleaved `float32` IQ pairs and converts them to `complex64`.
- The analyzer loads `.npy` files as `complex64`.

## Per-run checks

### f922000000_gain20_50db
- out: `noise_rx2a_gain20_50db.npy`
- backend: `uhd_rx_samples_to_file_fallback`
- selected channel: `0`
- selected antenna: `RX2`
- tuned frequency: `922000000.0`
- RX gain: `20.0`
- sample rate: `4000000.0`
- rx_samples_to_file command: `["/opt/homebrew/Cellar/uhd/4.10.0.0_1/lib/uhd/examples/rx_samples_to_file", "--freq", "922000000.0", "--rate", "4000000.0", "--gain", "20.0", "--duration", "10.0", "--ant", "RX2", "--subdev", "A:A", "--channels", "0", "--type", "float", "--file", "/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f922000000_gain20_50db/noise_rx2a_gain20_50db.npy.tmp.fc32"]`
- output size bytes: `320000000`
- expected samples: `40000000`
- actual parsed samples: `40000000`
- parser dtype: `float32_interleaved_iq_to_complex64`
- size matches expected: `True`
- out: `txon_rx2a_gain20_50db.npy`
- backend: `uhd_rx_samples_to_file_fallback`
- selected channel: `0`
- selected antenna: `RX2`
- tuned frequency: `922000000.0`
- RX gain: `20.0`
- sample rate: `4000000.0`
- rx_samples_to_file command: `["/opt/homebrew/Cellar/uhd/4.10.0.0_1/lib/uhd/examples/rx_samples_to_file", "--freq", "922000000.0", "--rate", "4000000.0", "--gain", "20.0", "--duration", "30.0", "--ant", "RX2", "--subdev", "A:A", "--channels", "0", "--type", "float", "--file", "/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f922000000_gain20_50db/txon_rx2a_gain20_50db.npy.tmp.fc32"]`
- output size bytes: `960000000`
- expected samples: `120000000`
- actual parsed samples: `120000000`
- parser dtype: `float32_interleaved_iq_to_complex64`
- size matches expected: `True`

### f923200000_gain20_50db
- out: `noise_rx2a_gain20_50db.npy`
- backend: `uhd_rx_samples_to_file_fallback`
- selected channel: `0`
- selected antenna: `RX2`
- tuned frequency: `923200000.0`
- RX gain: `20.0`
- sample rate: `4000000.0`
- rx_samples_to_file command: `["/opt/homebrew/Cellar/uhd/4.10.0.0_1/lib/uhd/examples/rx_samples_to_file", "--freq", "923200000.0", "--rate", "4000000.0", "--gain", "20.0", "--duration", "10.0", "--ant", "RX2", "--subdev", "A:A", "--channels", "0", "--type", "float", "--file", "/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f923200000_gain20_50db/noise_rx2a_gain20_50db.npy.tmp.fc32"]`
- output size bytes: `320000000`
- expected samples: `40000000`
- actual parsed samples: `40000000`
- parser dtype: `float32_interleaved_iq_to_complex64`
- size matches expected: `True`
- out: `txon_rx2a_gain20_50db.npy`
- backend: `uhd_rx_samples_to_file_fallback`
- selected channel: `0`
- selected antenna: `RX2`
- tuned frequency: `923200000.0`
- RX gain: `20.0`
- sample rate: `4000000.0`
- rx_samples_to_file command: `["/opt/homebrew/Cellar/uhd/4.10.0.0_1/lib/uhd/examples/rx_samples_to_file", "--freq", "923200000.0", "--rate", "4000000.0", "--gain", "20.0", "--duration", "30.0", "--ant", "RX2", "--subdev", "A:A", "--channels", "0", "--type", "float", "--file", "/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f923200000_gain20_50db/txon_rx2a_gain20_50db.npy.tmp.fc32"]`
- output size bytes: `960000000`
- expected samples: `120000000`
- actual parsed samples: `120000000`
- parser dtype: `float32_interleaved_iq_to_complex64`
- size matches expected: `True`

### f924400000_gain20_50db
- out: `noise_rx2a_gain20_50db.npy`
- backend: `uhd_rx_samples_to_file_fallback`
- selected channel: `0`
- selected antenna: `RX2`
- tuned frequency: `924400000.0`
- RX gain: `20.0`
- sample rate: `4000000.0`
- rx_samples_to_file command: `["/opt/homebrew/Cellar/uhd/4.10.0.0_1/lib/uhd/examples/rx_samples_to_file", "--freq", "924400000.0", "--rate", "4000000.0", "--gain", "20.0", "--duration", "10.0", "--ant", "RX2", "--subdev", "A:A", "--channels", "0", "--type", "float", "--file", "/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f924400000_gain20_50db/noise_rx2a_gain20_50db.npy.tmp.fc32"]`
- output size bytes: `320000000`
- expected samples: `40000000`
- actual parsed samples: `40000000`
- parser dtype: `float32_interleaved_iq_to_complex64`
- size matches expected: `True`
- out: `txon_rx2a_gain20_50db.npy`
- backend: `uhd_rx_samples_to_file_fallback`
- selected channel: `0`
- selected antenna: `RX2`
- tuned frequency: `924400000.0`
- RX gain: `20.0`
- sample rate: `4000000.0`
- rx_samples_to_file command: `["/opt/homebrew/Cellar/uhd/4.10.0.0_1/lib/uhd/examples/rx_samples_to_file", "--freq", "924400000.0", "--rate", "4000000.0", "--gain", "20.0", "--duration", "30.0", "--ant", "RX2", "--subdev", "A:A", "--channels", "0", "--type", "float", "--file", "/Users/laizhendong/Desktop/LEO-Hybrid-PGRL/hardware_conducted_iq/20260625_224417_debug_scan_50db/f924400000_gain20_50db/txon_rx2a_gain20_50db.npy.tmp.fc32"]`
- output size bytes: `960000000`
- expected samples: `120000000`
- actual parsed samples: `120000000`
- parser dtype: `float32_interleaved_iq_to_complex64`
- size matches expected: `True`
