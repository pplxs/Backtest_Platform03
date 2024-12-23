
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_performance_signal(date_position,output_path):
    # 创建图表
    fig = go.Figure()
    # 添加K线图
    fig.add_trace(go.Candlestick(
        x=date_position['date'],
        open=date_position['open'],
        high=date_position['high'],
        low=date_position['low'],
        close=date_position['close'],
        name='Price'
    ))

    # 筛选出有信号的日期
    specific_dates = date_position[date_position['signal'] != 0]['date']
    # 在close线上方添加注释
    for date in specific_dates:
        low = np.round(date_position.loc[date_position['date'] == date, 'low'].values[0], 2)
        high = np.round(date_position.loc[date_position['date'] == date, 'high'].values[0], 2)
        position_value = int(date_position.loc[date_position['date']==date, 'position'])
        signal_value = int(date_position.loc[date_position['date']==date, 'signal'])

        # 调整箭头方向
        ay_value = 0
        y_value = 0
        if signal_value==1:
            signal = 'buy'
            ay_value = 50
            y_value = low
        elif signal_value==-1:
            signal='sell'
            ay_value=-50
            y_value = high

        fig.add_annotation(
            x=date,
            y=y_value,  # 将文本放置在最低价的95%位置，确保在K线下方
            text=f"Position: {position_value} <br> Signal: {signal}",
            showarrow=True,
            arrowhead=2,
            ax=0,  # 水平偏移量，0表示箭头尾部与点对齐
            ay=ay_value,  # 垂直偏移量，根据需要调整这个值以确保注释在曲线正上方
            font=dict(size=12, color="Black"),
            align="center",
            arrowcolor="#636363",
            arrowwidth=2  # 调整箭头宽度
        )
    # 添加累积收益率线
    fig.add_trace(go.Scatter(
        x=date_position['date'],
        y=date_position['cum_returns'],
        yaxis='y2',  # 使用第二个y轴
        mode='lines',
        name='Cumulative Returns',
        line=dict(color='black',width=2)  # 设置线条颜色为黑色
    ))

    # 更新布局，增加边距和设置网格
    fig.update_layout(
        title='Price and Cumulative Returns',
        xaxis_title='Date',
        yaxis=dict(
            title='Price',
            showgrid=True,  # 显示网格
            gridcolor='rgba(200,200,200,0.5)',  # 设置网格颜色为浅灰色，半透明
            gridwidth=1  # 设置网格线的宽度
        ),
        yaxis2=dict(
            title='Cumulative Returns',
            overlaying='y',
            side='right',
            showgrid=True,  # 显示网格
            gridcolor='rgba(200,200,200,0.5)',  # 设置网格颜色为浅灰色，半透明
            gridwidth=1  # 设置网格线的宽度
        ),
        legend=dict(
                orientation="h",  # 图例水平显示
                x=0,  # 图例x位置
                xanchor="left",  # 图例x锚点
                y=0,  # 图例y位置
                yanchor="bottom",  # 图例y锚点
                # bgcolor='rgba(255,255,255,255,1)'  # 图例背景颜色
            ),
        margin=dict(l=10, r=10, t=50, b=10),  # 设置边距为0，使图表铺满页面
        width=1250,  # 设置图表宽度
        height=600,  # 设置图表高度
        dragmode='pan'  # 允许拖动时间轴
    )

    fig.write_html(output_path)
