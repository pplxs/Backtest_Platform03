import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_performance_overview(data_performance, output_path):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Strategy Cumulative Returns', 'Drawdown', 'Daily Returns')
    )

    # 添加数据到子图
    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["strategy_cum_returns"], name='Strategy Returns'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["benchmark_cum_returns"], name='Benchmark Returns'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["excess_returns"], name='Excess Returns'), row=1, col=1)

    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["strategy_drawdown"], name='Strategy Drawdown'), row=2, col=1)
    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["benchmark_drawdown"], name='Benchmark Drawdown'), row=2, col=1)

    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["strategy_returns"], name='Strategy Daily Returns'), row=3, col=1)
    fig.add_trace(go.Scatter(x=data_performance["date"], y=data_performance["benchmark_returns"], name='Benchmark Daily Returns'), row=3, col=1)

    # 更新布局
    fig.update_layout(
        title='Returns and Drawdown Analysis',
        height=900,
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                thickness=0.05
            ),
            type="date"
        )
    )

    # 为每个子图单独设置图例位置
    # fig.update_layout(
    #     legend=dict(
    #         orientation="h",
    #         yanchor="top",
    #         y=1.02,
    #         xanchor="left",
    #         x=0.01,
    #         xref="paper", yref="paper"
    #     )
    # )

    fig.write_html(output_path)
    # fig.show()

if __name__ == "__main__":
    data_performance = {
        "date": pd.date_range(start='2024-01-01', periods=100),
        "strategy_returns": np.random.normal(0, 0.01, 100),
        "strategy_cum_returns": np.cumsum(np.random.normal(0, 0.01, 100)),
        "strategy_drawdown": np.random.normal(-0.02, 0.01, 100),
        "benchmark_returns": np.random.normal(0, 0.01, 100),
        "benchmark_cum_returns": np.cumsum(np.random.normal(0, 0.01, 100)),
        "benchmark_drawdown": np.random.normal(-0.02, 0.01, 100),
        "excess_returns": np.random.normal(0, 0.01, 100)
    }

    create_performance_overview(data_performance, 'performance_overview.html')