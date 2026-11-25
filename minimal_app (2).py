#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 19:33:35 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# Page configuration, title and data source
st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout='wide')
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# Data Ingestion
app_dir = Path(__file__).resolve().parent
data_paths = [
    app_dir / "data" / "world_happiness_2023.csv",
    app_dir.parent / "data" / "world_happiness_2023.csv",
]
data_path = next((path for path in data_paths if path.is_file()), None)
if data_path is None:
    st.error("Missing dataset. Add world_happiness_2023.csv to the repository's data folder.")
    st.stop()

df = pd.read_csv(data_path)

df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

factor_labels = {
    "GDP": "GDP per capita",
    "Social_Support": "Social support",
    "Life_Expectancy": "Healthy life expectancy",
    "Freedom": "Freedom to make life choices",
    "Generosity": "Generosity",
    "Corruption": "Perceptions of corruption",
}

# Side bar filters
with st.sidebar:
    st.header("Filters")
    regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)
    st.divider()
    st.caption("Each dot is a country in the selected region. Hover over a dot to see its values.")
    factor = st.selectbox("Factor to compare", options=list(factor_labels), format_func=factor_labels.get)
    

# filter data by region and top_n
filtered = df if selected_region == 'All Regions' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')

# KPI row 
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# create top bar chart
fig = px.bar(top, x='Score', y='Country', orientation='h',
             labels={'Score': 'Happiness Score (0–10)', 'Country': ''},
             template='plotly_white', title=f'Happiest {len(top)} Countries in 2023 - {selected_region}')

fig.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                  xaxis=dict(range=[0, 10]), height=600)


st.plotly_chart(fig, width="stretch") 

st.divider()
st.subheader("Happiness and its contributing factors")

scatter = px.scatter(
    filtered,
    x=factor,
    y="Score",
    color="Region",
    hover_name="Country",
    labels={factor: factor_labels[factor], "Score": "Happiness score (0–10)"},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Safe,
)
scatter.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color="white")))
scatter.update_layout(
    height=440,
    margin=dict(l=8, r=8, t=12, b=8),
    legend=dict(orientation="h", y=-0.24, title_text=""),
    showlegend=selected_region == "All Regions",
)
scatter.update_yaxes(range=[0, 10])
st.plotly_chart(scatter, width="stretch")
st.divider()
st.caption("Built with Streamlit + Plotly")