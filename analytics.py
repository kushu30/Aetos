# analytics.py
import pandas as pd
import networkx as nx
from itertools import combinations

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
    """Analyzes keyword co-occurrence to find technology convergence."""
    # Create a new graph
    G = nx.Graph()
    
    # Iterate through each document's keywords
    for keywords_list in df['keywords']:
        # Create unique pairs of keywords (combinations) from the list
        for word1, word2 in combinations(keywords_list, 2):
            if G.has_edge(word1, word2):
                # If the edge already exists, increase its weight
                G[word1][word2]['weight'] += 1
            else:
                # Otherwise, add a new edge with a weight of 1
                G.add_edge(word1, word2, weight=1)

    # Get all edges and their weights
    if not G.edges(data=True):
        return []

    # Sort the edges by weight in descending order
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
    
    # Format the top N results
    top_convergences = [
        {"tech_1": edge[0], "tech_2": edge[1], "strength": edge[2]['weight']}
        for edge in sorted_edges[:top_n]
    ]
    
    return top_convergences