import os
import sys
from .reports import quantstats as qs


def create_performance_returns(strategy_name,symbol, returns,benchmark_returns,BASE_DIR,ann_risk_free):
    dirs = str(
            BASE_DIR) + '\\' + f'templates/backtest/reports/{strategy_name}/'
    os.makedirs(dirs,exist_ok=True)
    output_path = dirs + strategy_name + '_' + symbol + '_returns.html'
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    qs.extend_pandas()
    qs.reports.html(
        returns,
        rf=ann_risk_free,  # risk-free ratio
        output=output_path,
        template_path=str(BASE_DIR) + '\\' + 'backtest/evaluator/report_generator/reports/quantstats/new_report.html',
        max_width=20,
        max_height=8,
        btc_price=benchmark_returns)
    return output_path