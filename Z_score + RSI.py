from numpy.matrixlib import defmatrix
import numpy as np
import pandas as pd

def compute_signal (df: pd.DataFrame) -> pd.DataFrame:
    df= df.copy()
    rolling_mean =df['close'].rolling(window=20).mean()
    rolling_std = df['close'].rolling(window=20).std()
    df['z_score'] = (df['close']-rolling_mean)/rolling_std

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta<0,0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['rsi'] = 100 - (100 / (1 + rs))

    df['signal'] = 0
    df.loc[(df['z_score'] < -2.0) & (df['rsi'] < 35), 'signal'] = 1 
    df.loc[df['z_score'] >= 0.0, 'signal'] = 0  

    conditions = [
        (df['z_score'] < -2.0) & (df['rsi'] < 35), 
        (df['z_score'] >= 0.0)                     
    ]
    choices = [1, 0]
    df['action'] = np.select(conditions, choices, default=np.nan)
    df['position'] = df['action'].ffill().fillna(0).shift(1).fillna(0)
    return df
def back_test(df:pd.DataFrame , cost_per_trade : float = 0.0015) -> dict[str, float]:
    df = df.copy()
    df['market_ret'] = df['close'].pct_change().fillna(0)
    trades_diff = df['position'].diff().abs().fillna(0)
    df['strategy_ret'] = (
      df['position'] * df['market_ret'] - trades_diff * cost_per_trade
  )
    df['cum_ret'] = (1 + df['strategy_ret']).cumprod()
    df['peak'] = df['cum_ret'].cummax()
    df['drawdown'] = (df['cum_ret'] - df['peak']) / df['peak']
    total_ret = df['cum_ret'].iloc[-1] - 1
    n_days = len(df)
    if n_days > 0 and (1 + total_ret) > 0:
        cagr = (1 + total_ret) ** (252 / n_days) - 1 
    else: cagr = 0.0

    std = df['strategy_ret'].std()
    if std > 0:
        sharpe = (np.sqrt(252)*df['strategy_ret'].mean())/(std+1e-9)
    else: sharpe = 0.0

    max_dd = df['drawdown'].min()

    is_new_trade = (df['position'] == 1) & (df['position'].shift(1, fill_value=0) == 0)
    df['trade_id'] = is_new_trade.cumsum()
    active_trades = df[df['position'] == 1]
    trade_pnls = active_trades.groupby('trade_id')['strategy_ret'].apply(lambda r: (1 + r).prod() - 1).tolist()

    wins = [p for p in trade_pnls if p > 0]
    losses = [p for p in trade_pnls if p < 0]

    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (np.inf if gross_profit > 0 else 0.0)
    win_rate = len(wins) / len(trade_pnls) if trade_pnls else 0.0
    
    calmar = (cagr / abs(max_dd)) if max_dd != 0 else 0.0

    return {
      'Total Return': f'{total_ret * 100:.2f}%',
      'Sharpe Ratio': f'{sharpe:.2f}',
      'CAGR': f'{cagr * 100:.1f}%',
      'Max Drawdown': f'{max_dd * 100:.1f}%',
      'Profit factor': f'{profit_factor:.2f}',
      'Calmar': f'{calmar:.2f}',
    }

if __name__ == '__main__':
    from vnstock.api.quote import Quote

    symbol = 'HPG'
    print(f'>> Đang tải dữ liệu cổ phiếu {symbol}...')
    q = Quote(symbol=symbol, source='VCI')
    df = q.history(start='2023-01-01', end='2024-12-31')

    df_with_signals = compute_signal(df)
    results = back_test(df_with_signals)
    print(f'\n=== KẾT QUẢ BACKTEST CHIẾN LƯỢC ({symbol}) ===')
    for metric, value in results.items():
        print(f'{metric:<16}: {value}')





