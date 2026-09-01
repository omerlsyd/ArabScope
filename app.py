import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="ArabScope",
    page_icon="assets/arabscope_logo.png",
    layout="wide"
)

header_col1, header_col2 = st.columns([0.5, 4])

with header_col1:
    st.image(
        "assets/arabscope_logo.png",
        width=85
    )

with header_col2:
    st.markdown(
        "<h1 style='margin-top: 0px;'>ArabScope</h1>",
        unsafe_allow_html=True
    )

    st.caption(
        "Explore • Compare • Understand Arab Economies"
    )

# World Bank indicators
INDICATORS = {
    "GDP": "NY.GDP.MKTP.CD",
    "GDP per capita": "NY.GDP.PCAP.CD",
    "GDP growth": "NY.GDP.MKTP.KD.ZG",
    "Inflation": "FP.CPI.TOTL.ZG"
}

COUNTRIES = {
    "Egypt": "EGY",
    "Saudi Arabia": "SAU",
    "UAE": "ARE",
    "Qatar": "QAT",
    "Morocco": "MAR",
    "Jordan": "JOR"
}

@st.cache_data
def get_world_bank_data(country_code, indicator):

    url = (
        f"https://api.worldbank.org/v2/country/"
        f"{country_code}/indicator/{indicator}"
        f"?format=json&per_page=100"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return pd.DataFrame()

        data = response.json()

        if len(data) < 2:
            return pd.DataFrame()

        records = []

        for item in data[1]:

            if item["value"] is not None:

                records.append({
                    "Year": int(item["date"]),
                    "Value": item["value"]
                })

        return pd.DataFrame(records)

    except requests.exceptions.RequestException:

        return pd.DataFrame()

    except (ValueError, KeyError, TypeError):

        return pd.DataFrame()


# Sidebar

st.sidebar.header("Explore Arab Economies")

mode = st.sidebar.radio(
    "View",
    [
        "Country Profile",
        "Country Comparison",
        "About ArabScope"
    ]
)

if mode == "Country Profile":

    selected_country = st.sidebar.selectbox(
        "Country:",
        list(COUNTRIES.keys())
    )

    selected_year = st.sidebar.number_input(
        "Year:",
        min_value=1960,
        max_value=2025,
        value=2024,
        step=1
    )


elif mode == "Country Comparison":

    selected_countries = st.sidebar.multiselect(
        "Countries:",
        list(COUNTRIES.keys()),
        default=["Egypt", "UAE"],
        key="comparison_countries"
    )

    comparison_year = st.sidebar.number_input(
        "Year:",
        min_value=1960,
        max_value=2025,
        value=2024,
        step=1
    )

# Main content

if mode == "Country Profile":

    st.header(f"{selected_country} — Economic Overview ({selected_year})")

    country_code = COUNTRIES[selected_country]

    profile_tab, charts_tab = st.tabs(
        ["Overview", "Historical Data"]
    )

    # =========================
    # OVERVIEW TAB
    # =========================

    with profile_tab:

        indicator_data = {}

        for indicator_name, indicator_code in INDICATORS.items():

            data = get_world_bank_data(
                country_code,
                indicator_code
            )

            if not data.empty:

                year_data = data[
                    data["Year"] == selected_year
                ]

                if not year_data.empty:
                    indicator_data[indicator_name] = (
                        year_data.iloc[0]
                    )

        # KPI CARDS

        st.subheader("Key Economic Indicators")

        col1, col2, col3, col4 = st.columns(4)

        # GDP
        if "GDP" in indicator_data:

            value = indicator_data["GDP"]["Value"]

            col1.metric(
                f"GDP ({selected_year})",
                f"${value / 1e9:.1f}B"
            )

        else:

            col1.metric(
                f"GDP ({selected_year})",
                "Not available"
            )

        # GDP Growth
        if "GDP growth" in indicator_data:

            value = indicator_data["GDP growth"]["Value"]

            col2.metric(
                f"GDP Growth ({selected_year})",
                f"{value:.2f}%"
            )

        else:

            col2.metric(
                f"GDP Growth ({selected_year})",
                "Not available"
            )

        # GDP per Capita
        if "GDP per capita" in indicator_data:

            value = indicator_data["GDP per capita"]["Value"]

            col3.metric(
                f"GDP per Capita ({selected_year})",
                f"${value:,.0f}"
            )

        else:

            col3.metric(
                f"GDP per Capita ({selected_year})",
                "Not available"
            )

        # Inflation
        if "Inflation" in indicator_data:

            value = indicator_data["Inflation"]["Value"]

            col4.metric(
                f"Inflation ({selected_year})",
                f"{value:.2f}%"
            )

        else:

            col4.metric(
                f"Inflation ({selected_year})",
                "Not available"
            )

    # =========================
    # HISTORICAL TRENDS TAB
    # =========================

    with charts_tab:

        def show_indicator_chart(
            indicator_name,
            country_code
        ):

            data = get_world_bank_data(
                country_code,
                INDICATORS[indicator_name]
            )

            if not data.empty:

                st.subheader(
                    f"{indicator_name} Over Time"
                )

                st.line_chart(
                    data,
                    x="Year",
                    y="Value"
                )

            else:

                st.info(
                    f"{indicator_name} data is not available."
                )

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:

            show_indicator_chart(
                "GDP",
                country_code
            )

            show_indicator_chart(
                "GDP per capita",
                country_code
            )


        with trend_col2:

            show_indicator_chart(
                "GDP growth",
                country_code
            )

            show_indicator_chart(
                "Inflation",
                country_code
            )

elif mode == "Country Comparison":


    # =========================
    # COUNTRY COMPARISON
    # =========================

    if len(selected_countries) < 2:

        st.warning(
            "Please select at least two countries."
        )

    else:

        st.header(
            f"Compare Arab Economies — {comparison_year}"
            
        )

        st.caption(
            "Compare key economic indicators across selected countries."
        )

        comparison_data = []

        for country in selected_countries:

            country_code = COUNTRIES[country]

            country_record = {
                "Country": country
            }

            for indicator_name, indicator_code in INDICATORS.items():

                data = get_world_bank_data(
                    country_code,
                    indicator_code
                )

                if not data.empty:

                    year_data = data[
                        data["Year"] == comparison_year
                    ]

                    if not year_data.empty:

                        country_record[indicator_name] = (
                            year_data.iloc[0]["Value"]
                        )

                    else:

                        country_record[indicator_name] = None

                else:

                    country_record[indicator_name] = None

            comparison_data.append(country_record)

        comparison_df = pd.DataFrame(
            comparison_data
        )
        

        # =========================
        # COMPARISON TABLE
        # =========================

        st.subheader("Economic Indicators")

        display_df = comparison_df.copy()

        # Format comparison table

        formatted_df = display_df.copy()
        
        if "GDP" in formatted_df.columns:
            formatted_df["GDP"] = formatted_df["GDP"].apply(
                lambda x: (
                    f"${x / 1e9:.1f}B"
                    if pd.notna(x)
                    else "Not available"
                )
            )

        if "GDP growth" in formatted_df.columns:
            formatted_df["GDP growth"] = formatted_df["GDP growth"].apply(
                lambda x: (
                    f"{x:.2f}%"
                    if pd.notna(x)
                    else "Not available"
                )
            )

        if "GDP per capita" in formatted_df.columns:
            formatted_df["GDP per capita"] = formatted_df["GDP per capita"].apply(
                lambda x: (
                    f"${x:,.0f}"
                    if pd.notna(x)
                    else "Not available"
                )
            )

        if "Inflation" in formatted_df.columns:
            formatted_df["Inflation"] = formatted_df["Inflation"].apply(
                lambda x: (
                    f"{x:.2f}%"
                    if pd.notna(x)
                    else "Not available"
                )
            )

        st.dataframe(
            formatted_df,
            use_container_width=True,
            hide_index=True
        )

                # =========================
        # ECONOMIC ANALYSIS
        # =========================

        st.subheader("Economic Analysis")

        st.caption(
            f"Based on available data for {comparison_year}."
        )

        for indicator in INDICATORS.keys():

            available_data = comparison_df[
                ["Country", indicator]
            ].dropna()

            if len(available_data) >= 2:

                highest = available_data.loc[
                    available_data[indicator].idxmax()
                ]

                lowest = available_data.loc[
                    available_data[indicator].idxmin()
                ]

                st.write(
                    f"**{INDICATORS.get(indicator, indicator)}:** "
                    f"{highest['Country']} has the highest value "
                    f"({highest[indicator]:,.2f})."
                )

                st.write(
                    f"Lowest: {lowest['Country']} "
                    f"({lowest[indicator]:,.2f})."
                )

            else:

                st.write(
                    f"**{INDICATORS.get(indicator, indicator)}:** "
                    f"Not enough data available for comparison."
                )

                        # =========================
        # COMPARISON CHARTS
        # =========================

        st.subheader("Visual Comparison")

        st.caption(
            f"Comparison of selected countries in {comparison_year}."
        )
        chart_indicators = [
            "GDP",
            "GDP growth",
            "GDP per capita",
            "Inflation"
        ]

        for indicator in chart_indicators:

            chart_data = comparison_df[
                ["Country", indicator]
            ].dropna()

            if not chart_data.empty:

                chart_data = chart_data.set_index("Country")

                st.write(f"**{INDICATORS.get(indicator, indicator)}**")

                st.bar_chart(
                    chart_data[indicator]
                )

            else:

                st.info(
                    f"{indicator} data is not available."
                )

elif mode == "About ArabScope":

    st.header("What is ArabScope?")

    st.write(
        """
        ArabScope is an interactive economic
        data dashboard designed to explore and compare key
        economic indicators across countries.
        """
    )

    st.subheader("Data Sources")

    st.write(
        """
        The economic data used in this application comes from
        the World Bank Open Data API.
        """
    )

    st.subheader("Economic Indicators")

    st.markdown(
        """
        - **GDP:** Total economic output of a country.
        - **GDP Growth:** Annual percentage growth of GDP.
        - **GDP per Capita:** GDP divided by the population.
        - **Inflation:** Annual percentage change in consumer prices.
        """
    ) 

st.divider()

st.caption(
    "Data source: World Bank Open Data"
)         