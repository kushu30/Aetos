# analytics.py
import pandas as pd
import numpy as np
import networkx as nx
from itertools import combinations
from sklearn.linear_model import LinearRegression

def calculate_s_curve(df: pd.DataFrame) -> list:
    """Calculates the S-curve data from a dataframe of documents."""
    df['published_date'] = pd.to_datetime(df['published'], errors='coerce')
    df.dropna(subset=['published_date'], inplace=True)
    if df.empty:
        return []

    df['year'] = df['published_date'].dt.year
    yearly_counts = df['year'].value_counts().sort_index()
    cumulative_counts = yearly_counts.cumsum()
    
    s_curve_data = []
    for year, count in yearly_counts.items():
        s_curve_data.append({
            'year': int(year),
            'count': int(count),
            'cumulative_count': int(cumulative_counts.loc[year])
        })
    return s_curve_data

def find_technology_convergence(df: pd.DataFrame, top_n: int = 10) -> list:
    """Analyzes technology co-occurrence to find technology convergence."""
    # Ensure technologies column exists and contains lists
    if 'technologies' not in df.columns:
        return []
    
    df_tech = df.dropna(subset=['technologies'])
    
    G = nx.Graph()
    
    for tech_list in df_tech['technologies']:
        if isinstance(tech_list, list) and len(tech_list) > 1:
            for tech1, tech2 in combinations(sorted(tech_list), 2):
                if G.has_edge(tech1, tech2):
                    G[tech1][tech2]['weight'] += 1
                else:
                    G.add_edge(tech1, tech2, weight=1)

    if not G.edges(data=True):
        return []

    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    
    top_convergences = [
        {"tech_1": edge[0], "tech_2": edge[1], "strength": edge[2]['weight']}
        for edge in sorted_edges[:top_n]
    ]
    
    return top_convergences

def calculate_trl_progression(df: pd.DataFrame) -> dict:
    """Calculates historical TRL progression and provides a simple forecast."""
    df['published_date'] = pd.to_datetime(df['published'], errors='coerce')
    df.dropna(subset=['published_date', 'TRL'], inplace=True)
    df = df[df['TRL'] > 0]
    if df.empty or len(df) < 2:
        return {"history": [], "forecast": []}

    df['year'] = df['published_date'].dt.year
    
    # Calculate historical average TRL per year
    yearly_trl = df.groupby('year')['TRL'].mean().round(2).sort_index()
    
    history = [{'year': int(year), 'avg_trl': trl} for year, trl in yearly_trl.items()]

    # Simple Linear Regression for Forecasting
    X = yearly_trl.index.values.reshape(-1, 1)
    y = yearly_trl.values
    
    forecast = []
    if len(X) > 1: # Need at least 2 points to forecast
        model = LinearRegression()
        model.fit(X, y)

        # Forecast for the next 3 years
        last_year = X.max()
        future_years = np.arange(last_year + 1, last_year + 4).reshape(-1, 1)
        future_trl = model.predict(future_years).round(2)
        
        # Ensure forecast doesn't exceed TRL 9
        future_trl[future_trl > 9] = 9.0

        forecast = [{'year': int(year), 'avg_trl': trl} for year, trl in zip(future_years.flatten(), future_trl)]

    return {"history": history, "forecast": forecast}