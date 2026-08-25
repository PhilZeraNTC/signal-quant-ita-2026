import asyncio
import numpy as np
import pandas as pd

class Backtester:
    def __init__(self, initial_capital=10000.0, transaction_cost_bps=5.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = 0.0
        self.transaction_cost_bps = transaction_cost_bps
        self.portfolio_history = []
        
    async def execute_trade(self, price, target_weight):
        portfolio_value = self.cash + self.positions * price
        target_position_value = portfolio_value * target_weight
        current_position_value = self.positions * price
        
        trade_value = target_position_value - current_position_value
        trade_shares = trade_value / price
        
        transaction_cost = abs(trade_value) * (self.transaction_cost_bps / 10000.0)
        
        self.cash -= (trade_value + transaction_cost)
        self.positions += trade_shares

    async def run_backtest(self, data_stream, risk_agent):
        async for point in data_stream:
            # Signal generation at t_close (no lookahead)
            target_weight = await risk_agent.allocate_capital(point)
            
            # Execute at t+1_open
            await self.execute_trade(point['t_plus_1_open'], target_weight)
            
            # Record MTM at t+1_open
            portfolio_value = self.cash + self.positions * point['t_plus_1_open']
            self.portfolio_history.append({
                'date': point['date'],
                'portfolio_value': portfolio_value
            })
            
    def calculate_metrics(self):
        if not self.portfolio_history:
            return 0.0, 0.0
            
        df = pd.DataFrame(self.portfolio_history)
        df['returns'] = df['portfolio_value'].pct_change()
        
        mean_return = df['returns'].mean()
        std_return = df['returns'].std()
        
        if std_return > 0:
            sharpe_ratio = (mean_return / std_return) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0
            
        df['cumulative_max'] = df['portfolio_value'].cummax()
        df['drawdown'] = (df['portfolio_value'] - df['cumulative_max']) / df['cumulative_max']
        max_drawdown = df['drawdown'].min()
        
        return sharpe_ratio, max_drawdown
