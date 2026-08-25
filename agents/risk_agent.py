import asyncio
from collections import deque

class RiskAgent:
    def __init__(self, target_vol=0.15, max_adjustments=2):
        self.target_vol = target_vol
        self.max_adjustments = max_adjustments
        self.adjustment_indices = deque()
        self.current_day_index = 0
        self.current_weight = 0.0
        
    async def allocate_capital(self, data_point):
        """
        Calculates capital allocation using inverse volatility targeting and sentiment tilt.
        Base_Weight = Target_Vol / Forecast_Vol
        Final_Weight = Base_Weight * (1 + sentiment * conviction_factor)
        """
        self.current_day_index += 1
        
        # Clean up old adjustments (older than 21 trading days)
        while self.adjustment_indices and self.adjustment_indices[0] <= self.current_day_index - 21:
            self.adjustment_indices.popleft()
            
        forecast_vol = data_point.get('forecast_vol', 0.15)
        sentiment = data_point.get('sentiment', 0.0)
        conviction_factor = data_point.get('conviction_factor', 1.0)
        
        if forecast_vol <= 0:
            proposed_weight = 0.0
        else:
            base_weight = self.target_vol / forecast_vol
            proposed_weight = base_weight * (1 + sentiment * conviction_factor)
            
        # Check if we need to adjust and if we are allowed to
        # Threshold to avoid micro-adjustments counting towards the limit
        if abs(proposed_weight - self.current_weight) > 0.01:
            if len(self.adjustment_indices) < self.max_adjustments:
                self.current_weight = proposed_weight
                self.adjustment_indices.append(self.current_day_index)
            else:
                # Limit reached, ignore signal and maintain current allocation
                pass 
                
        return self.current_weight
