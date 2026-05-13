# imports 
import pandas as pd
import matplotlib.pyplot as plt
import json
import plotly.express as px


#Function 1 creates baseline n_employment (2019) and merges it into the original dataframe
def add_baseline(

    df,
    value_col="n_employed",
    baseline_year=2019,
    geography_col="geography_label_value",
    group_cols=None,
    year_col="year_pd",
    baseline_col="baseline_emp"
):
    """
    Adds baseline employment values from a selected year to a dataframe.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing employment data.
    value_col : str, default="n_employed"
        Column containing the values used as the baseline.
    baseline_year : int, default=2019
        Year used as the baseline reference.
    geography_col : str, default="geography_label_value"
        Geography column used if no grouping columns are provided.
    group_cols : list, optional
        Columns used to match baseline values across groups.
        If None, geography_col is used.
    year_col : str, default="year_pd"
        Datetime column containing yearly observations.
    baseline_col : str, default="baseline_emp"
        Name of the output baseline column.
    Returns
    -------
    pandas.DataFrame
        Original dataframe merged with baseline values.
    """
    if group_cols is None:
        group_cols = [geography_col]

    baseline = (
        df[df[year_col].dt.year == baseline_year]
        [group_cols + [value_col]]
        .rename(columns={value_col: baseline_col})
    )

    return df.merge(
        baseline,
        on=group_cols,
        how="left"
    )

#Function 2 - Creates recovery index 
def add_recovery_index(
    df,
    current_col="n_employed",
    baseline_col="baseline_emp",
    recovery_col="recovery_index"
):
    """
    Calculates a recovery index relative to a baseline value.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing current and baseline values.
    current_col : str, default="n_employed"
        Column containing current values.
    baseline_col : str, default="baseline_emp"
        Column containing baseline values.
    recovery_col : str, default="recovery_index"
        Name of the output recovery index column.
    Returns
    -------
    pandas.DataFrame
        Dataframe with an added recovery index column,
        where baseline = 100.
    """
    df = df.copy()
    df[recovery_col] = (
        df[current_col] / df[baseline_col]
    ) * 100
    return df
    
# Function 3: visualization function for employment trends
def plot_trends(
    df,
    x_col,
    y_col,
    county_col,
    title,
    ylabel,
    save_path,
    figsize=(8, 6),
    legend_title=None,
    baseline=None,
    y_min=None,
    start_groups=None
):
    """
    Creates an interactive Plotly line chart for trend analysis.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing trend data.
    x_col : str
        Column used for the x-axis.
    y_col : str
        Column used for the y-axis.
    county_col : str
        Column used for grouping and coloring lines.
    title : str
        Chart title.
    ylabel : str
        Label for the y-axis.
    save_path : str
        File path used to save the interactive HTML chart.
    figsize : tuple, default=(8, 6)
        Figure size in inches.
    legend_title : str, optional
        Title displayed in the legend.
    baseline : float, optional
        Horizontal reference line value.
    y_min : float, optional
        Minimum y-axis value.
    start_groups : list, optional
        Groups shown initially on the chart.
        Other groups remain hidden but clickable in the legend.
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly figure.
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=county_col,
        title=title,
        labels={
            x_col: "Year",
            y_col: ylabel,
            county_col: legend_title
        },
        width=figsize[0] * 100,
        height=figsize[1] * 100,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        font_family="Georgia",
        font_size=14,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e5e5e5")
    fig.update_yaxes(showgrid=True, gridcolor="#e5e5e5")
    # baseline
    if baseline is not None:
        fig.add_hline(y=baseline)
    # y-axis minimum
    if y_min is not None:
        fig.update_yaxes(range=[y_min, None])
    else:
        fig.update_yaxes(range=[0, None])
    # Show only selected groups at start
    if start_groups is not None:
        for trace in fig.data:
            if trace.name not in start_groups:
                trace.visible = "legendonly"
    fig.write_html(save_path.replace(".png", ".html"))
    return fig


#Function 4: race 
def map_race_population(
    df: pd.DataFrame,
    race_col: str = "race",
    race_map: dict = None,
    output_col: str = "population_by_race",
) -> pd.DataFrame:
    """
     Maps race-specific population values into a single column.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing race codes and population columns.
    race_col : str, default="race".
    race_map : dict, 
        Dictionary mapping race codes to population columns.
        Example:
        {"A1": "pop_white","A2": "pop_black","A3": "pop_asian"
        }
    output_col : str, default="population_by_race"
        Name of the output column containing mapped population values.
    Returns
    -------
    pandas.DataFrame
        Dataframe with a new column containing the
        population value associated with each race code.
    """
    df = df.copy()
    df[output_col] = None

    for race_code, pop_col in race_map.items():
        df.loc[df[race_col] == race_code, output_col] = df[pop_col]

    return df



# Function 5: Jobs per capita by race
def plot_jobs_per_capita_by_race(
    df: pd.DataFrame,
    county_name: str,
    x_col: str = "year_pd",
    y_col: str = "jobs_per_capita",
    race_col: str = "race_label_value",
    county_col: str = "county",
    figsize: tuple[int, int] = (7, 6),
    save_folder: str = "visualizations"
):
    """
    Creates an interactive Plotly line chart showing jobs per capita by race
    for a selected county.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing jobs per capita by race and county.
    county_name : str
        County to filter for the chart.
    x_col : str, default="year_pd"
        Column used for the x-axis.
    y_col : str, default="jobs_per_capita"
        Column used for the y-axis.
    race_col : str, default="race_label_value"
        Column containing race group labels.
    county_col : str, default="county"
        Column containing county names.
    figsize : tuple, default=(7, 6)
        Figure size in inches.
    save_folder : str, default="visualizations"
        Folder where the interactive HTML chart is saved.
    Returns
    -------
    plotly.graph_objects.Figure
    Interactive Plotly figure.
    """
    county_subset = df[df[county_col] == county_name].copy()

    county_subset = county_subset[
        county_subset[race_col].isin([
            "White Alone",
            "Black or African American Alone",
            "Asian Alone"
        ])
    ]

    fig = px.line(
        county_subset,
        x=x_col,
        y=y_col,
        color=race_col,
        title=f"Jobs per Capita by Race ({county_name})",
        labels={
            x_col: "Year",
            y_col: "Jobs per Capita (total employed / total population)",
            race_col: "Race:"
        },
        width=figsize[0] * 100,
        height=figsize[1] * 100,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(mode="lines+markers")

    fig.update_layout(
        font_family="Georgia",
        font_size=14,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig.update_xaxes(showgrid=True, gridcolor="#e5e5e5")
    fig.update_yaxes(showgrid=True, gridcolor="#e5e5e5", range=[0, None])

    fig.write_html(f"{save_folder}/jobs_per_capita_race_{county_name}.html")

    return fig

#Function 6: ethnicity
def map_ethnicity_population(
    df: pd.DataFrame,
    ethnicity_col: str = "ethnicity",
    ethnicity_map: dict = None,
    output_col: str = "population_by_ethnicity",
) -> pd.DataFrame:

    """
    Maps ethnicity-specific population values into a single column.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing ethnicity codes and population columns.
    ethnicity_col : str, default="ethnicity"
        Column containing ethnicity codes.
    ethnicity_map : dict, optional
        Dictionary mapping ethnicity codes to population columns.
        Example:
        {"A0": "pop_hispanic"}
    output_col : str, default="population_by_ethnicity"
        Name of the output column containing mapped population values.
    Returns
    -------
    pandas.DataFrame
        Dataframe with a new column containing the
        population value associated with each ethnicity code.
    """
    df = df.copy()
    df[output_col] = None

    for ethnicity_code, pop_col in ethnicity_map.items():
        df.loc[df[ethnicity_col] == ethnicity_code, output_col] = df[pop_col]

    return df

# Function 7: plotting recovery index
# Defining function to make an interactive recovery chart that can be used for race, ethnicity, firm size, etc
def plot_recovery_trends(
    df,
    x_col,
    y_col,
    group_col,
    title,
    legendtitle,
    ylabel,
    save_path,
    baseline=100,
    y_min=85
):
    """
    Creates an interactive Plotly line chart for recovery index trends.
    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe containing recovery index data.
    x_col : str
        Column used for the x-axis.
    y_col : str
        Column used for the y-axis.
    group_col : str
        Column used for grouping and coloring lines.
    title : str
        Chart title.
    ylabel : str
        Label for the y-axis.
    save_path : str
        File path used to save the interactive HTML chart.
    baseline : float, default=100
        Baseline recovery value shown as a horizontal reference line.
    y_min : float, default=85
        Minimum y-axis value.
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly figure.
    """
    # Create line chart
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=group_col,
        title=title,
        labels={
            x_col: "Year",
            y_col: ylabel,
            group_col: ""
        },
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Add baseline line
    fig.add_hline(
        y=baseline,
        line_dash="dot",
        line_color="black",
        annotation_text=f"{baseline} baseline"
    )

    # Style lines and markers
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=2.5),
        marker=dict(size=6),

        hovertemplate=
        "<b>%{fullData.name}</b><br>"
        "Year: %{x}<br>"
        f"{ylabel}: " + "%{y:.1f}<extra></extra>"
    )

    # Layout styling
    fig.update_layout(
        font_family="Georgia",
        font_size=14,
        plot_bgcolor="white",
        paper_bgcolor="white",

        yaxis=dict(
            range=[y_min, None],
            gridcolor="#f0f0f0"
        ),

        xaxis=dict(
            gridcolor="#f0f0f0"
        ),

        legend=dict(
            title=legendtitle,
            x=1.02,
            y=1
        )
    )
    return fig

    # Save
    save_path = f"{save_folder}/jobs_per_capita_{county_name}.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
    return fig, ax


