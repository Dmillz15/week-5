import streamlit as st
import plotly.graph_objects as go

from apputil import *
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')
import pandas as pd
import plotly.express as px

# Load Titanic dataset
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')

def survival_demographics():
    """
    Analyze survival patterns by passenger class, sex, and age group.
    Returns a DataFrame with passenger counts, survivor counts, and survival rates.
    """
    # Age categories
    bins = [0, 12, 19, 59, 100]
    labels = ['Child', 'Teen', 'Adult', 'Senior']
    df['age_group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True)
    
    grouped = df.groupby(['Pclass', 'Sex', 'age_group']).agg(
        n_passengers=('PassengerId', 'count'),
        n_survivors=('Survived', 'sum')
    ).reset_index()
    
    grouped['survival_rate'] = (grouped['n_survivors'] / grouped['n_passengers']).round(3)
    
    grouped = grouped.sort_values(['Pclass', 'Sex', 'age_group'])
    
    return grouped

def visualize_demographic():
    """
    Create a visualization with distinct colors for men and women
    showing survival rates across passenger classes and age groups.
    """
    data = survival_demographics()
    
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
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
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

fig1 = visualize_demographic()
st.plotly_chart(fig1, use_container_width=True)


fig1_2 = visualize_gender_comparison()
st.plotly_chart(fig1_2, use_container_width=True)

st.write(
'''
# Titanic Visualization 2
'''
)

# Load Titanic dataset
df = pd.read_csv('https://raw.githubusercontent.com/leontoddjohnson/datasets/main/data/titanic.csv')

st.write(
'''
# Titanic Visualization 1 - Family Analysis

**Research Question:** How did family size and passenger class interact to affect ticket fares, and were larger families concentrated in specific classes with distinct fare patterns?

'''
)

def family_groups():
    """
    Analyze family size, passenger class, and ticket fare relationships.
    """
    df['family_size'] = df['SibSp'] + df['Parch'] + 1
    
    grouped = df.groupby(['family_size', 'Pclass']).agg(
        n_passengers=('PassengerId', 'count'),
        avg_fare=('Fare', 'mean'),
        min_fare=('Fare', 'min'),
        max_fare=('Fare', 'max')
    ).reset_index()
    
    grouped['avg_fare'] = grouped['avg_fare'].round(2)
    grouped['min_fare'] = grouped['min_fare'].round(2)
    grouped['max_fare'] = grouped['max_fare'].round(2)
    
    grouped = grouped.sort_values(['Pclass', 'family_size'])
    
    return grouped

def last_names():
    """
    Extract last names from the Name column and return counts for each last name.
    """
    # Extract last names (everything before the comma)
    df['last_name'] = df['Name'].str.split(',').str[0].str.strip()
    
    # Count occurrences of each last name
    last_name_counts = df['last_name'].value_counts().reset_index()
    last_name_counts.columns = ['last_name', 'count']
    
    return last_name_counts

st.write("""
# Family Analysis of Titanic Survival

**Research Question:** How did family size and passenger class interact to affect ticket fares, and were larger families concentrated in specific classes with distinct fare patterns?
""")

def visualize_families():
    """
    Create a visualization exploring the relationship between family size, 
    passenger class, and ticket fares.
    """
    data = family_groups()
    
    # Create a bubble chart showing family size vs fare by class
    fig = px.scatter(
        data,
        x='family_size',
        y='avg_fare',
        size='n_passengers',
        color='Pclass',
        title='Family Size vs Average Ticket Fare by Passenger Class',
        labels={
            'family_size': 'Family Size',
            'avg_fare': 'Average Fare (£)',
            'Pclass': 'Passenger Class',
            'n_passengers': 'Number of Passengers'
        },
        category_orders={'Pclass': [1, 2, 3]},
        color_discrete_map={
            1: '#1f77b4',  # Blue for 1st class
            2: '#ff7f0e',  # Orange for 2nd class  
            3: '#2ca02c'   # Green for 3rd class
        },
        size_max=40,
        hover_data=['min_fare', 'max_fare']
    )
    
    # Customize layout
    fig.update_layout(
        height=500,
        showlegend=True,
        xaxis=dict(dtick=1),  # Ensure integer ticks for family size
        yaxis=dict(title='Average Fare (£)')
    )
    
    # Add trend lines for each class
    for pclass in [1, 2, 3]:
        class_data = data[data['Pclass'] == pclass]
        if len(class_data) > 1:
            fig.add_trace(
                go.Scatter(
                    x=class_data['family_size'],
                    y=class_data['avg_fare'],
                    mode='lines',
                    line=dict(dash='dot', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                )
            )
    
    return fig

def visualize_fare_ranges():
   
    data = family_groups()
    
    fig = px.bar(
        data,
        x='family_size',
        y='avg_fare',
        color='Pclass',
        facet_col='Pclass',
        title='Average Ticket Fare by Family Size and Passenger Class',
        labels={
            'family_size': 'Family Size',
            'avg_fare': 'Average Fare (£)',
            'Pclass': 'Passenger Class'
        },
        category_orders={'Pclass': [1, 2, 3]},
        color_discrete_map={
            1: '#1f77b4',
            2: '#ff7f0e', 
            3: '#2ca02c'
        }
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    fig.for_each_annotation(lambda a: a.update(text=f"Class {a.text.split('=')[1]}"))
    
    return fig

def visualize_large_families():
    """
    Focus on families with 4+ members to understand large family patterns.
    """
    data = family_groups()
    large_families = data[data['family_size'] >= 4]
    
    fig = px.bar(
        large_families,
        x='family_size',
        y='n_passengers',
        color='Pclass',
        title='Distribution of Large Families (4+ Members) by Passenger Class',
        labels={
            'family_size': 'Family Size',
            'n_passengers': 'Number of Passengers',
            'Pclass': 'Passenger Class'
        },
        category_orders={'Pclass': [1, 2, 3]},
        color_discrete_map={
            1: '#1f77b4',
            2: '#ff7f0e',
            3: '#2ca02c'
        }
    )
    
    fig.update_layout(height=400)
    return fig


fig2 = visualize_families()
st.plotly_chart(fig2, use_container_width=True)

st.write(
'''
# Titanic Visualization 2 - Fare Ranges
'''
)

# Generate and display the fare range visualization
fig3 = visualize_fare_ranges()
st.plotly_chart(fig3, use_container_width=True)

# Show the family groups data
st.write("### Family Groups Data")
family_data = family_groups()
st.dataframe(family_data)

# Show last name analysis
st.write("### Last Name Analysis")
last_name_data = last_names()
st.write("Top 20 Most Common Last Names:")
st.dataframe(last_name_data.head(20))

# Compare last name counts with family size analysis
st.write("### Comparison: Last Name Counts vs Family Size Analysis")

# Calculate average family size by class
avg_family_by_class = df.groupby('Pclass')['family_size'].mean().round(2)

st.write("**Average Family Size by Class:**")
st.write(avg_family_by_class)

st.write("**Key Findings:**")
st.write("""
- **Last Name Distribution**: The most common last names (Sage, Andersson, Asplund, etc.) appear 5-11 times, suggesting large family groups
- **Family Size Patterns**: Third class had the largest average family sizes, while first class had smaller families
- **Fare Structure**: First class families paid significantly higher fares regardless of family size
- **Large Families**: Families larger than 4 were almost exclusively in third class with lower average fares
- **Wealth Disparity**: The fare range within first class was much wider than other classes, indicating greater wealth variation among wealthy passengers
""")




fig4 = visualize_large_families()
st.plotly_chart(fig4, use_container_width=True)

# Generate and display the figure
fig5 = visualize_families()
st.plotly_chart(fig5, use_container_width=True)

st.write(
'''
# Titanic Visualization Bonus
'''
)
