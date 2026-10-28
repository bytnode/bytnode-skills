# Technical indicators (POST /v1/indicators)

> Generated from https://api.bytnode.com/openapi.json (contract **3.0.1**) by `tools/generate_references.py`. Do not edit by hand: regenerate.

POST a JSON body: `symbol`, `timeframe`, `limit` (values per indicator, 1 to 1000, default 1) and `indicators`, a list of `{id, type, <parameters flat>}` — e.g. `{"id": "rsi_14", "type": "rsi", "period": 14}`. `id` is your own name for the result (1 to 64 characters among letters, digits, `_`, `-`, `.`), unique in the call: `data.indicators` is keyed by it, and a type may appear any number of times. Parameters go FLAT in the indicator object; an unknown body field is a 422 `unknown_parameter`. Computed on the same candles as `/v1/klines/history`; `limit + warm-up` is capped at 1000 candles. Each result gives `values`: one row per candle, MOST RECENT FIRST like every list of the API — `{time, value}`, or the named outputs of a multi-output indicator (`{time, macd, signal, histogram}`). Errors on the indicators are 422 `invalid_indicator`. On a stablecoin: 200, `data: null`, `unavailable: "not_applicable"`.

## The 19 types

- **`ad`** (Accumulation/Distribution line): Warm-up: 0 candles before the first value. Output: one array of values. Uses the candle volume. No parameter.
- **`adosc`** (Chaikin A/D oscillator): Warm-up: 6×slow candles before the first value. Output: one array of values. Uses the candle volume. Parameters: `fast` default 3 minimum 2; `slow` default 10 minimum 5.
- **`adx`** (Average Directional Index): Warm-up: 14×period candles before the first value. Output: one array of values. Parameters: `period` default 14 minimum 2.
- **`atr`** (Average True Range): Warm-up: 5×period candles before the first value. Output: one array of values. Parameters: `period` default 14 minimum 2.
- **`bb`** (Bollinger Bands): Warm-up: period candles before the first value. Output: an object of arrays `upper, middle, lower`. Parameters: `period` default 20 minimum 2; `std` default 2.0 minimum 0.5, maximum 10.0.
- **`cci`** (Commodity Channel Index): Warm-up: period candles before the first value. Output: one array of values. Parameters: `period` default 20 minimum 2.
- **`donchian`** (Donchian channel): Warm-up: period candles before the first value. Output: an object of arrays `upper, middle, lower`. Parameters: `period` default 20 minimum 2.
- **`ema`** (Exponential moving average): Warm-up: 3×period candles before the first value. Output: one array of values. Parameters: `period` default 20 minimum 2.
- **`ichimoku`** (Ichimoku cloud): Warm-up: max(tenkan,kijun,senkou)+kijun candles before the first value. Output: an object of arrays `tenkan_sen, kijun_sen, senkou_a, senkou_b`. Parameters: `tenkan` default 9 minimum 2; `kijun` default 26 minimum 5; `senkou` default 52 minimum 10.
- **`keltner`** (Keltner channel): Warm-up: 5×period candles before the first value. Output: an object of arrays `upper, middle, lower`. Parameters: `period` default 20 minimum 2; `multiplier` default 2.0 minimum 0.5, maximum 10.0.
- **`macd`** (MACD): Warm-up: 3×slow+signal candles before the first value. Output: an object of arrays `macd, signal, histogram`. Parameters: `fast` default 12 minimum 2; `slow` default 26 minimum 5; `signal` default 9 minimum 2.
- **`mfi`** (Money Flow Index): Warm-up: period candles before the first value. Output: one array of values. Uses the candle volume. Parameters: `period` default 14 minimum 2.
- **`obv`** (On-Balance Volume): Warm-up: 0 candles before the first value. Output: one array of values. Uses the candle volume. No parameter.
- **`roc`** (Rate of change): Warm-up: period candles before the first value. Output: one array of values. Parameters: `period` default 10 minimum 2.
- **`rsi`** (Relative Strength Index): Warm-up: 5×period candles before the first value. Output: one array of values. Parameters: `period` default 14 minimum 2.
- **`sar`** (Parabolic SAR): Warm-up: 200 candles before the first value. Output: one array of values. Parameters: `acceleration` default 0.02 minimum 0.01, maximum 1.0; `maximum` default 0.2 minimum 0.05, maximum 1.0.
- **`sma`** (Simple moving average): Warm-up: period candles before the first value. Output: one array of values. Parameters: `period` default 20 minimum 2.
- **`stoch`** (Stochastic oscillator): Warm-up: k+d+smooth candles before the first value. Output: an object of arrays `k, d`. Parameters: `k` default 14 minimum 2; `d` default 3 minimum 2; `smooth` default 3 minimum 2.
- **`willr`** (Williams %R): Warm-up: period candles before the first value. Output: one array of values. Parameters: `period` default 14 minimum 2.
