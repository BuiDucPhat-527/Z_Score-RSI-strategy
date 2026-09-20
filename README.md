# Mean Reversion Quantitative Trading Strategy (Z-Score + RSI)

An institutional-grade quantitative research and backtesting framework developed for the Vietnamese equity market (HOSE/HNX), combining a statistical **Price Z-Score** model with the **Relative Strength Index (RSI)** momentum oscillator.

---

## 1. Strategy Rationale & Theoretical Foundation

The strategy operates on the economic principle of **Statistical Mean Reversion**: During severe selling pressures or market panics, equity prices frequently overshoot their intrinsic short-term equilibrium due to behavioral biases and forced liquidations. When prices deviate excessively below their historical moving average into deep oversold territory, mean-reverting forces and value-seeking capital typically trigger a strong corrective rebound.

### Statistical & Technical Indicators:

1. **Price Z-Score (Rolling 20-period lookback):**
   Measures the number of standard deviations ($\sigma$) that the current closing price deviates from its 20-day rolling mean ($\mu_{20}$):
   $$\text{Z-Score}_t = \frac{\text{Close}_t - \mu_{20, t}}{\sigma_{20, t}}$$

2. **Relative Strength Index (14-period RSI):**
   Quantifies price momentum and confirms exhaustion of downward momentum:
   $$\text{RS} = \frac{\text{SMA}(\text{Gain}, 14)}{\text{SMA}(\text{Loss}, 14) + \epsilon}, \quad \text{RSI} = 100 - \frac{100}{1 + \text{RS}}$$

---

## 2. Trading Rules & Signal Architecture

Tailored for the Vietnamese cash equity market, the system strictly enforces a **Long-Only** regime (no short selling):

| Action | Execution Trigger | Theoretical Justification |
| :--- | :--- | :--- |
| **Long Entry** | `Z-Score < -2.0` **AND** `RSI < 35` | Price is >2 standard deviations below the mean accompanied by deep oversold momentum. |
| **Exit / Flat** | `Z-Score >= 0.0` | Price reverts to or crosses above the 20-day moving average (equilibrium restored). |

### Holding State Machine & Look-Ahead Bias Prevention:
- **State Persistence:** Uses vectorized condition evaluation (`np.select`) chained with forward-fill (`.ffill()`) to maintain position continuity from entry to exit.
- **No Look-Ahead Bias:** Signals generated at bar close $T$ are lagged via `.shift(1)` to ensure trades are executed at the opening or subsequent prices on bar $T+1$.

---

## 3. Backtesting Framework & Key Performance Metrics

The backtester calculates realistic portfolio equity curves by explicitly incorporating transaction friction:
- **Transaction Cost:** `0.15%` ($0.0015$) applied on each position transition (turnover on both entry and exit).

### The 5 Target Quantitative Metrics (+ Total Return):

| Metric | Mathematical Definition | Institutional Significance |
| :--- | :--- | :--- |
| **Total Return** | $\frac{\text{Equity}_N}{\text{Equity}_0} - 1$ | Cumulative net return over the entire backtesting horizon. |
| **Sharpe Ratio** | $\sqrt{252} \times \frac{\mathbb{E}[R_{\text{strategy}}]}{\sigma(R_{\text{strategy}})}$ | Annualized risk-adjusted return relative to total volatility. |
| **CAGR** | $(1 + \text{Total Return})^{\frac{252}{N}} - 1$ | Compound Annual Growth Rate normalized per 252 trading days. |
| **Maximum Drawdown (MDD)** | $\min_t \left( \frac{\text{Equity}_t - \text{Peak}_t}{\text{Peak}_t} \right)$ | The peak-to-trough maximum observed portfolio equity loss. |
| **Profit Factor** | $\frac{\sum \text{Gross Profits}}{\sum \|\text{Gross Losses}\|}$ | Ratio of aggregate winning trade volume to aggregate losing volume. |
| **Calmar Ratio** | $\frac{\text{CAGR}}{\|\text{Max Drawdown}\|}$ | Ratio of annualized return to maximum historical drawdown risk. |

---

## 4. Repository Structure

```text
.
├── Z_score + RSI.py    # Core strategy module: Signal generation, backtest engine & execution
└── README.md           # Comprehensive quantitative documentation and quickstart guide
```

---

## 5. Installation & Usage

### Prerequisites
- Python >= 3.10
- Dependencies: `pandas`, `numpy`, `vnstock`

```bash
pip install pandas numpy vnstock
```

### Running the Backtest
Run the strategy directly via terminal or through your IDE:

```bash
python "Z_score + RSI.py"
```

### Sample Output (Ticker: `HPG`, Period: 2023 – 2024):
```text
>> Đang tải dữ liệu cổ phiếu HPG...

=== KẾT QUẢ BACKTEST CHIẾN LƯỢC (HPG) ===
Total Return    : 2.56%
Sharpe Ratio    : 0.17
CAGR            : 1.2%
Max Drawdown    : -13.0%
Profit factor   : 1.48
Calmar          : 0.09
```

### Customizing Ticker & Date Range
Open `Z_score + RSI.py` and modify the execution block at the bottom of the script:

```python
symbol = 'FPT'  # e.g., SSI, VCB, VNM, MWG
q = Quote(symbol=symbol, source='VCI')
df = q.history(start='2022-01-01', end='2024-12-31')
```

---

## 6. Future Extensions

1. **Risk Management Overlay:** Add hard stop-loss thresholds (e.g., $Z < -3.5$) or trailing stop mechanisms to cap downside tail risk.
2. **Microstructure Adaptation (T+2.5):** Implement explicit settlement lock states simulating the Vietnamese T+2.5 delivery cycle.
3. **Multi-Asset VN30 Portfolio:** Expand the single-stock engine into a dynamic portfolio scanner across the entire VN30 basket with volatility-weighted position sizing.
