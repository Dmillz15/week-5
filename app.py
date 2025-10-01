import streamlit as st
import plotly.graph_objects as go

from apputil import *
# Load Titanic dataset
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load Titanic dataset
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')

def survival_demographics():
    """
    Analyze survival patterns by passenger class, sex, and age group.
    Returns a DataFrame with passenger counts, survivor counts, and survival rates.
    """
    # Create age categories using pd.cut()
    bins = [0, 12, 19, 59, 100]
    labels = ['Child', 'Teen', 'Adult', 'Senior']
    df['age_group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    
    # Group by class, sex, and age group
    grouped = df.groupby(['Pclass', 'Sex', 'age_group']).agg(
        n_passengers=('PassengerId', 'count'),
        n_survivors=('Survived', 'sum')
    ).reset_index()
    
    # Calculate survival rate
    grouped['survival_rate'] = (grouped['n_survivors'] / grouped['n_passengers']).round(3)
    
    # Order results for easy interpretation
    grouped = grouped.sort_values(['Pclass', 'Sex', 'age_group'])
    
    return grouped

def visualize_demographic():
    """
    Create a visualization with distinct colors for men and women
    showing survival rates across passenger classes and age groups.
    """
    data = survival_demographics()
    
    # Create a grouped bar chart with distinct colors for genders
    fig = px.bar(
        data,
        x='Pclass',
        y='survival_rate',
        color='Sex',
        facet_col='age_group',
        facet_col_wrap=2,
        title='Titanic Survival Rates: Women vs Men Across Classes and Age Groups',
        labels={
            'survival_rate': 'Survival Rate',
            'Pclass': 'Passenger Class',
            'Sex': 'Gender',
            'age_group': 'Age Group'
        },
        category_orders={
            'Pclass': [1, 2, 3],
            'Sex': ['female', 'male'],
            'age_group': ['Child', 'Teen', 'Adult', 'Senior']
        },
        barmode='group',
        color_discrete_map={
            'female': '#FF6B9C',  # Pink for women
            'male': '#4A90E2'     # Blue for men
        }
    )
    
    # Customize the layout
    fig.update_layout(
        yaxis_tickformat=',.0%',
        yaxis_range=[0, 1.1],
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update facet labels to be more readable
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # Add value labels on bars
    for i, row in data.iterrows():
        class_offset = -0.2 if row['Sex'] == 'female' else 0.2
        facet_col = ['Child', 'Teen', 'Adult', 'Senior'].index(row['age_group'])
        
        fig.add_annotation(
            x=row['Pclass'] + class_offset,
            y=row['survival_rate'] + 0.05,
            text=f"{row['survival_rate']:.0%}",
            showarrow=False,
            font=dict(size=10, color='black'),
            xref=f"x{facet_col+1 if facet_col > 0 else ''}",
            yref=f"y{facet_col+1 if facet_col > 0 else ''}"
        )
    
    return fig
def visualize_gender_comparison():
    data = survival_demographics()
    
    # Calculate the difference in survival rates between women and men
    women_data = data[data['Sex'] == 'female'].set_index(['Pclass', 'age_group'])
    men_data = data[data['Sex'] == 'male'].set_index(['Pclass', 'age_group'])
    
    comparison_data = women_data[['survival_rate']].copy()
    comparison_data.columns = ['women_survival_rate']
    comparison_data['men_survival_rate'] = men_data['survival_rate']
    comparison_data['survival_difference'] = comparison_data['women_survival_rate'] - comparison_data['men_survival_rate']
    comparison_data = comparison_data.reset_index()
    
    fig = px.bar(
        comparison_data,
        x='survival_difference',
        y='age_group',
        color='survival_difference',
        facet_col='Pclass',
        title='Survival Advantage: Women vs Men Across Classes and Age Groups',
        labels={
            'survival_difference': 'Survival Rate Advantage for Women',
            'age_group': 'Age Group',
            'Pclass': 'Passenger Class'
        },
        color_continuous_scale='RdYlBu',
        range_color=[-1, 1]
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis=dict(tickformat=',.0%'),
        xaxis_title="Women's Survival Advantage Over Men"
    )
    
    fig.for_each_annotation(lambda a: a.update(text=f"Class {a.text.split('=')[1]}"))
    
    for i in range(1, 4):
        fig.add_vline(x=0, line_dash="dash", line_color="black", 
                     row=1, col=i)
    
    return fig
st.write(
'''
# Titanic Visualization 1 - Demographic Analysis

**Research Question:** How did the survival rates for women and children compare across different passenger classes, and were there situations where class privilege significantly altered expected survival patterns?

'''
)

# Generate and display the figure
fig1 = visualize_demographic()
st.plotly_chart(fig1, use_container_width=True)


fig1_2 = visualize_gender_comparison()
st.plotly_chart(fig1_2, use_container_width=True)

st.write(
'''
# Titanic Visualization 2
'''
)
# Generate and display the figure
fig2 = visualize_families()
st.plotly_chart(fig2, use_container_width=True)

st.write(
'''
# Titanic Visualization Bonus
'''
)
# Generate and display the figure
fig3 = visualize_family_size()
st.plotly_chart(fig3, use_container_width=True)