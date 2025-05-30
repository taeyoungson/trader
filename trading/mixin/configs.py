
class TargetObjectiveMixin:
    _maximum_trading_number_of_stocks: int
    _target_profit_rate: float


class BuyStrategyMixin:
    _ratio_remainder_to_total: float = 0.5
