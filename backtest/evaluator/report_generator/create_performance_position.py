

import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_performance_position(data_performance_position, output_path):

    dates = data_performance_position["date"]
    balance = data_performance_position["balance"]
    position = data_performance_position["position"]
    benchmark_price = data_performance_position["benchmark_price"]
    # 创建图表
    fig = go.Figure()

    # 添加持仓区域图
    fig.add_trace(go.Scatter(
        x=dates,
        y=position,
        fill='tozeroy',
        fillcolor='orange',
        line=dict(color='rgba(0,0,0,0)'),  # 设置边界线为无色
        name='position'
    ))

    # 添加资金线
    fig.add_trace(go.Scatter(
        x=dates,
        y=balance,
        line=dict(color='red', width=2),
        name='balance'
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=benchmark_price,
        line=dict(color='blue', width=2),
        name='BTCUSDT Price'
    ))

    # 更新布局
    fig.update_layout(
        title='all assets',
        xaxis_title='date',
        yaxis_title='asset value',
        height=600,
        showlegend=True
    )

    # fig.show()
    fig.write_html(output_path)