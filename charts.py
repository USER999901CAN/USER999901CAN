"""Interactive Plotly charts for retirement planning"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


def create_balance_projection_chart(df, retirement_age):
    """Create interactive balance projection chart"""
    fig = go.Figure()
    
    # Add balance line
    fig.add_trace(go.Scatter(
        x=df['Age'],
        y=df['Investment Balance End'],
        mode='lines',
        name='Investment Balance',
        line=dict(color='#2E86AB', width=3),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Balance: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add lump sum markers
    lump_sum_df = df[df['Lump Sum'] > 0]
    if not lump_sum_df.empty:
        fig.add_trace(go.Scatter(
            x=lump_sum_df['Age'],
            y=lump_sum_df['Investment Balance End'],
            mode='markers',
            name='Lump Sum Received',
            marker=dict(size=12, color='rgb(46, 204, 113)', symbol='star'),
            hovertemplate='<b>Age %{x}</b><br>' +
                          'Lump Sum: $%{customdata:,.0f}<br>' +
                          'Balance After: $%{y:,.0f}<br>' +
                          '<extra></extra>',
            customdata=lump_sum_df['Lump Sum']
        ))
    
    # Add lump sum withdrawal markers
    lump_withdrawal_df = df[df['Lump Sum Withdrawal'] > 0]
    if not lump_withdrawal_df.empty:
        fig.add_trace(go.Scatter(
            x=lump_withdrawal_df['Age'],
            y=lump_withdrawal_df['Investment Balance End'],
            mode='markers',
            name='Lump Sum Withdrawal',
            marker=dict(size=12, color='rgb(231, 76, 60)', symbol='x'),
            hovertemplate='<b>Age %{x}</b><br>' +
                          'Withdrawal: $%{customdata:,.0f}<br>' +
                          'Balance After: $%{y:,.0f}<br>' +
                          '<extra></extra>',
            customdata=lump_withdrawal_df['Lump Sum Withdrawal']
        ))
    
    # Add retirement age marker
    fig.add_vline(
        x=retirement_age,
        line_dash="dash",
        line_color="green",
        annotation_text="Retirement",
        annotation_position="top"
    )
    
    # Add zero line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="red",
        opacity=0.5
    )
    
    fig.update_layout(
        title='Investment Balance Over Time',
        xaxis_title='Age',
        yaxis_title='Balance ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig


def create_income_sources_chart(df, retirement_age):
    """Create stacked area chart of income sources"""
    retirement_df = df[df['Age'] >= retirement_age].copy()
    
    fig = go.Figure()
    
    # Add income sources as stacked areas
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['Part-Time Income'],
        mode='lines',
        name='Part-Time Income',
        stackgroup='one',
        fillcolor='rgba(46, 134, 171, 0.5)',
        line=dict(width=0.5, color='rgb(46, 134, 171)'),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Part-Time: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['Monthly Pension'],
        mode='lines',
        name='Pension',
        stackgroup='one',
        fillcolor='rgba(168, 218, 220, 0.5)',
        line=dict(width=0.5, color='rgb(168, 218, 220)'),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Pension: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['Investment Withdrawal'],
        mode='lines',
        name='Investment Withdrawal',
        stackgroup='one',
        fillcolor='rgba(241, 196, 15, 0.5)',
        line=dict(width=0.5, color='rgb(241, 196, 15)'),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Withdrawal: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add lump sums as scatter points (not stacked)
    lump_sum_df = retirement_df[retirement_df['Lump Sum'] > 0]
    if not lump_sum_df.empty:
        fig.add_trace(go.Scatter(
            x=lump_sum_df['Age'],
            y=lump_sum_df['Lump Sum'],
            mode='markers',
            name='Lump Sum',
            marker=dict(size=12, color='rgb(46, 204, 113)', symbol='star'),
            hovertemplate='<b>Age %{x}</b><br>' +
                          'Lump Sum: $%{y:,.0f}<br>' +
                          '<extra></extra>'
        ))
    
    # Add lump sum withdrawals as scatter points
    lump_withdrawal_df = retirement_df[retirement_df['Lump Sum Withdrawal'] > 0]
    if not lump_withdrawal_df.empty:
        fig.add_trace(go.Scatter(
            x=lump_withdrawal_df['Age'],
            y=lump_withdrawal_df['Lump Sum Withdrawal'],
            mode='markers',
            name='Lump Sum Withdrawal',
            marker=dict(size=12, color='rgb(231, 76, 60)', symbol='x'),
            hovertemplate='<b>Age %{x}</b><br>' +
                          'Withdrawal: $%{y:,.0f}<br>' +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        title='Monthly Income Sources in Retirement',
        xaxis_title='Age',
        yaxis_title='Monthly Income ($)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig


def create_withdrawal_vs_4pct_chart(df, retirement_age):
    """Create chart comparing withdrawals to 4% rule"""
    retirement_df = df[df['Age'] >= retirement_age].copy()
    
    fig = go.Figure()
    
    # Add 4% rule line first (so it's behind)
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['4% Rule Amount'],
        mode='lines',
        name='4% Rule (Safe)',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate='<b>Age %{x}</b><br>' +
                      '4% Rule: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add actual withdrawal line
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['Investment Withdrawal'],
        mode='lines',
        name='Your Withdrawal',
        line=dict(color='#2E86AB', width=3),
        fill='tonexty',  # Fill to previous trace (4% rule)
        fillcolor='rgba(255, 0, 0, 0.2)',  # Red fill where withdrawal > 4% rule
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Withdrawal: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title='Withdrawal Rate vs 4% Rule',
        xaxis_title='Age',
        yaxis_title='Monthly Withdrawal ($)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig


def create_purchasing_power_chart(df, retirement_age):
    """Create chart showing income in today's dollars"""
    retirement_df = df[df['Age'] >= retirement_age].copy()
    
    fig = go.Figure()
    
    # Nominal income
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['Total Monthly Income'],
        mode='lines',
        name='Nominal Income',
        line=dict(color='#2E86AB', width=2),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Nominal: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # Real income (today's dollars)
    fig.add_trace(go.Scatter(
        x=retirement_df['Age'],
        y=retirement_df['Income (Today\'s $)'],
        mode='lines',
        name='Real Income (Today\'s $)',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Real: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title='Purchasing Power: Nominal vs Real Income',
        xaxis_title='Age',
        yaxis_title='Monthly Income ($)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig


def create_monte_carlo_percentile_chart(mc_results, retirement_age):
    """Create interactive Monte Carlo percentile chart"""
    ages = list(mc_results['percentile_data'].keys())
    p10 = [mc_results['percentile_data'][age]['p10'] for age in ages]
    p25 = [mc_results['percentile_data'][age]['p25'] for age in ages]
    p50 = [mc_results['percentile_data'][age]['p50'] for age in ages]
    p75 = [mc_results['percentile_data'][age]['p75'] for age in ages]
    p90 = [mc_results['percentile_data'][age]['p90'] for age in ages]
    
    fig = go.Figure()
    
    # Add percentile bands
    fig.add_trace(go.Scatter(
        x=ages + ages[::-1],
        y=p90 + p10[::-1],
        fill='toself',
        fillcolor='rgba(46, 134, 171, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='10th-90th Percentile',
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=ages + ages[::-1],
        y=p75 + p25[::-1],
        fill='toself',
        fillcolor='rgba(46, 134, 171, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        name='25th-75th Percentile',
        hoverinfo='skip'
    ))
    
    # Add median line
    fig.add_trace(go.Scatter(
        x=ages,
        y=p50,
        mode='lines',
        name='Median (50th)',
        line=dict(color='#2E86AB', width=3),
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Median: $%{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add retirement marker
    fig.add_vline(
        x=retirement_age,
        line_dash="dash",
        line_color="green",
        annotation_text="Retirement",
        annotation_position="top"
    )
    
    # Add zero line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="red",
        opacity=0.5
    )
    
    fig.update_layout(
        title='Monte Carlo Simulation: Balance Projections',
        xaxis_title='Age',
        yaxis_title='Investment Balance ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig


def create_failure_age_histogram(mc_results):
    """Create interactive histogram of failure ages"""
    if not mc_results['failure_ages']:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=mc_results['failure_ages'],
        nbinsx=30,
        marker_color='#E74C3C',
        opacity=0.7,
        hovertemplate='<b>Age %{x}</b><br>' +
                      'Failures: %{y}<br>' +
                      '<extra></extra>'
    ))
    
    # Add average line
    avg_failure = mc_results['avg_failure_age']
    fig.add_vline(
        x=avg_failure,
        line_dash="dash",
        line_color="darkred",
        annotation_text=f"Avg: {avg_failure:.0f}",
        annotation_position="top"
    )
    
    fig.update_layout(
        title='Distribution of Failure Ages',
        xaxis_title='Age at Failure',
        yaxis_title='Number of Scenarios',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def create_dashboard_summary(df, inputs, results):
    """Create multi-panel dashboard summary"""
    retirement_age = inputs['retirement_age']
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Balance Over Time',
            'Income Sources',
            'Withdrawal vs 4% Rule',
            'Purchasing Power'
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Balance projection
    fig.add_trace(
        go.Scatter(x=df['Age'], y=df['Investment Balance End'],
                   mode='lines', name='Balance',
                   line=dict(color='#2E86AB', width=2)),
        row=1, col=1
    )
    
    # Add lump sum markers to balance chart
    lump_sum_df = df[df['Lump Sum'] > 0]
    if not lump_sum_df.empty:
        fig.add_trace(
            go.Scatter(x=lump_sum_df['Age'], y=lump_sum_df['Investment Balance End'],
                       mode='markers', name='Lump Sum',
                       marker=dict(size=8, color='rgb(46, 204, 113)', symbol='star')),
            row=1, col=1
        )
    
    # Add lump sum withdrawal markers to balance chart
    lump_withdrawal_df = df[df['Lump Sum Withdrawal'] > 0]
    if not lump_withdrawal_df.empty:
        fig.add_trace(
            go.Scatter(x=lump_withdrawal_df['Age'], y=lump_withdrawal_df['Investment Balance End'],
                       mode='markers', name='Lump Withdrawal',
                       marker=dict(size=8, color='rgb(231, 76, 60)', symbol='x')),
            row=1, col=1
        )
    
    # Income sources (retirement only)
    retirement_df = df[df['Age'] >= retirement_age]
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['Part-Time Income'],
                   mode='lines', name='Part-Time', stackgroup='one',
                   line=dict(width=0.5)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['Monthly Pension'],
                   mode='lines', name='Pension', stackgroup='one',
                   line=dict(width=0.5)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['Investment Withdrawal'],
                   mode='lines', name='Withdrawal', stackgroup='one',
                   line=dict(width=0.5)),
        row=1, col=2
    )
    
    # Withdrawal vs 4% rule
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['4% Rule Amount'],
                   mode='lines', name='4% Rule',
                   line=dict(color='green', dash='dash')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['Investment Withdrawal'],
                   mode='lines', name='Your Withdrawal',
                   line=dict(color='#2E86AB')),
        row=2, col=1
    )
    
    # Purchasing power
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['Total Monthly Income'],
                   mode='lines', name='Nominal',
                   line=dict(color='#2E86AB')),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=retirement_df['Age'], y=retirement_df['Income (Today\'s $)'],
                   mode='lines', name='Real',
                   line=dict(color='green', dash='dash')),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        template='plotly_white',
        hovermode='x unified'
    )
    
    # Update all y-axes to show currency format
    fig.update_yaxes(tickformat='$,.0f')
    
    return fig
