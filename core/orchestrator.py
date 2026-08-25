import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional
from agents.quant_agent import QuantAgent
from agents.genai_agent import FundamentalAgent

class Orchestrator:
    def __init__(
        self, 
        ticker: str,
        market_data: pd.DataFrame, 
        news_data: List[Dict[str, Any]], 
        backtest_start_date: str, 
        quant_agent: QuantAgent, 
        fundamental_agent: FundamentalAgent
    ):
        self.ticker = ticker
        self.market_data = market_data
        self.news_data = news_data
        self.backtest_start_date = pd.to_datetime(backtest_start_date)
        if self.backtest_start_date.tzinfo is None and self.market_data.index.tzinfo is not None:
            self.backtest_start_date = self.backtest_start_date.tz_localize(self.market_data.index.tzinfo)

        self.quant_agent = quant_agent
        self.fundamental_agent = fundamental_agent

    def prepare_agents(self):
        """
        Extract market data strictly before backtest_start_date and train the QuantAgent.
        """
        train_data = self.market_data[self.market_data.index < self.backtest_start_date].copy()
        
        # We need a target to train on. Since align_for_prediction is no longer called in main.py,
        # we generate the future volatility target here on the training set.
        train_data['Target_Vol_Future'] = train_data['Realized_Vol'].shift(-21)
        train_data = train_data.dropna(subset=['Target_Vol_Future'])
        
        features = [col for col in train_data.columns if col not in [
            'Target_Vol_Future', 'Close', 'Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'
        ]]
        
        X_train = train_data[features]
        y_train = train_data['Target_Vol_Future']
        
        if len(X_train) > 0:
            self.quant_agent.optimize(X_train, y_train)
            self.quant_agent.train(X_train, y_train)

    async def generate_events(self):
        """
        Async generator yielding daily point-in-time events.
        """
        test_data = self.market_data[self.market_data.index >= self.backtest_start_date]
        
        for i in range(len(test_data)):
            date = test_data.index[i]
            row = test_data.iloc[i]
            
            # Slice market data up to t_close
            history_up_to_t = self.market_data[self.market_data.index <= date]
            
            if len(history_up_to_t) == 0:
                continue
                
            features = [col for col in history_up_to_t.columns if col not in [
                'Target_Vol_Future', 'Close', 'Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'
            ]]
            X_current = history_up_to_t[features].iloc[-1:]
            
            # Predict volatility
            try:
                forecast_vol = self.quant_agent.predict(X_current)[0]
            except ValueError:
                forecast_vol = 0.15
            
            # Slice news up to t_close
            date_end_of_day = pd.Timestamp(date).replace(hour=23, minute=59, second=59)
            if date_end_of_day.tzinfo is None:
                date_end_of_day = date_end_of_day.tz_localize('UTC')
                
            headlines = []
            for item in self.news_data:
                pub_time = item.get('parsed_publish_time')
                if pub_time:
                    if pub_time.tzinfo is None:
                        pub_time = pub_time.tz_localize('UTC')
                    if pub_time <= date_end_of_day:
                        title = item.get('title', item.get('headline', ''))
                        if title:
                            headlines.append(title)
            
            # Use only recent headlines to keep context reasonable
            headlines = headlines[-10:]
            
            sentiment_output = await self.fundamental_agent.analyze_nday_batch(self.ticker, headlines, n_days=1)
            
            # Get t+1 open for execution. If it's the last day, use close.
            if i + 1 < len(test_data):
                t_plus_1_open = test_data.iloc[i + 1].get('Open', row['Close'])
            else:
                t_plus_1_open = row['Close']
            
            yield {
                'date': date,
                't_close': row['Close'],
                't_plus_1_open': t_plus_1_open,
                'forecast_vol': forecast_vol,
                'sentiment': sentiment_output.sentiment,
                'conviction_factor': 1.0
            }
