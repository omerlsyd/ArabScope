import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="ArabScope",
    page_icon="assets/arabscope_logo.png",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================

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


# =========================================================
# WORLD BANK INDICATORS
# =========================================================

INDICATORS = {
    "GDP": {
        "code": "NY.GDP.MKTP.CD",
        "unit": "USD",
        "type": "direct"
    },

    "GDP per capita": {
        "code": "NY.GDP.PCAP.CD",
        "unit": "USD",
        "type": "direct"
    },

    "GDP growth": {
        "code": "NY.GDP.MKTP.KD.ZG",
        "unit": "%",
        "type": "direct"
    },

    "Inflation": {
        "code": "FP.CPI.TOTL.ZG",
        "unit": "%",
        "type": "direct"
    },

    "Population": {
        "code": "SP.POP.TOTL",
        "unit": "people",
        "type": "direct"
    },

    "Exports": {
        "code": "NE.EXP.GNFS.CD",
        "unit": "USD",
        "type": "direct"
    },

    "Imports": {
        "code": "NE.IMP.GNFS.CD",
        "unit": "USD",
        "type": "direct"
    },

    "Trade Balance": {
        "code": None,
        "unit": "USD",
        "type": "calculated"
    },

    "Agriculture": {
        "code": "NV.AGR.TOTL.ZS",
        "unit": "%",
        "type": "direct"
    },

    "Industry": {
        "code": "NV.IND.TOTL.ZS",
        "unit": "%",
        "type": "direct"
    },

    "Services": {
        "code": "NV.SRV.TOTL.ZS",
        "unit": "%",
        "type": "direct"
    }
}


COUNTRIES = {
    "Algeria": "DZA",
    "Bahrain": "BHR",
    "Comoros": "COM",
    "Djibouti": "DJI",
    "Egypt": "EGY",
    "Iraq": "IRQ",
    "Jordan": "JOR",
    "Kuwait": "KWT",
    "Lebanon": "LBN",
    "Libya": "LBY",
    "Mauritania": "MRT",
    "Morocco": "MAR",
    "Oman": "OMN",
    "Palestine": "PSE",
    "Qatar": "QAT",
    "Saudi Arabia": "SAU",
    "Somalia": "SOM",
    "Sudan": "SDN",
    "Syria": "SYR",
    "Tunisia": "TUN",
    "UAE": "ARE",
    "Yemen": "YEM"
}


# =========================================================
# DATA FUNCTIONS
# =========================================================

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


# =========================================================
# FORMATTING FUNCTIONS
# =========================================================

def format_billions(value):

    if pd.isna(value):
        return "Not available"

    return f"${value / 1e9:.1f}B"


def format_currency(value):

    if pd.isna(value):
        return "Not available"

    return f"${value:,.0f}"


def format_percentage(value):

    if pd.isna(value):
        return "Not available"

    return f"{value:.2f}%"


def format_population(value):

    if pd.isna(value):
        return "Not available"

    return f"{value:,.0f}"


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Explore Arab Economies")

mode = st.sidebar.radio(
    "View",
    [
        "Country Profile",
        "Country Comparison",
        "Regional Analysis",
        "About ArabScope"
    ]
)


if mode == "Country Profile":

    selected_country = st.sidebar.selectbox(
        "Country:",
        list(COUNTRIES.keys())
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

elif mode == "Regional Analysis":

    regional_indicator = st.sidebar.selectbox(
        "Indicator:",
        [
            indicator
            for indicator, info in INDICATORS.items()
            if info["type"] == "direct"
        ],
        key="regional_indicator"
    )

    regional_year = st.sidebar.number_input(
        "Year:",
        min_value=1960,
        max_value=2025,
        value=2024,
        step=1,
        key="regional_year"
    )

# =========================================================
# COUNTRY PROFILE
# =========================================================

if mode == "Country Profile":

    country_code = COUNTRIES[selected_country]

    profile_tab, charts_tab = st.tabs(
        ["Overview", "Historical Data"]
    )


    # =====================================================
    # OVERVIEW
    # =====================================================

    with profile_tab:

        st.subheader("Overview Year")

        selected_year = st.number_input(
            "Year:",
            min_value=1960,
            max_value=2025,
            value=2024,
            step=1,
            key="overview_year"
        )

        st.header(
            f"{selected_country} — Economic Overview"
        )

        indicator_data = {}

        # ---------------------------------------------
        # Get all indicators
        # ---------------------------------------------

        for indicator_name, indicator_info in INDICATORS.items():

            if indicator_info["type"] == "calculated":
                continue

            data = get_world_bank_data(
                country_code,
                indicator_info["code"]
            )

            if not data.empty:

                year_data = data[
                    data["Year"] == selected_year
                ]

                if not year_data.empty:

                    indicator_data[indicator_name] = (
                        year_data.iloc[0]["Value"]
                    )


        # ---------------------------------------------
        # Calculate Trade Balance
        # ---------------------------------------------

        exports_value = indicator_data.get("Exports")
        imports_value = indicator_data.get("Imports")

        if (
            exports_value is not None
            and imports_value is not None
        ):

            indicator_data["Trade Balance"] = (
                exports_value - imports_value
            )


        # =================================================
        # KEY ECONOMIC INDICATORS
        # =================================================

        st.subheader("Key Economic Indicators")

        col1, col2, col3, col4 = st.columns(4)


        # GDP

        if "GDP" in indicator_data:

            col1.metric(
                f"GDP",
                format_billions(
                    indicator_data["GDP"]
                )
            )

        else:

            col1.metric(
                f"GDP",
                "Not available"
            )


        # GDP Growth

        if "GDP growth" in indicator_data:

            col2.metric(
                f"GDP Growth",
                format_percentage(
                    indicator_data["GDP growth"]
                )
            )

        else:

            col2.metric(
                f"GDP Growth",
                "Not available"
            )


        # GDP per Capita

        if "GDP per capita" in indicator_data:

            col3.metric(
                f"GDP per Capita",
                format_currency(
                    indicator_data["GDP per capita"]
                )
            )

        else:

            col3.metric(
                f"GDP per Capita",
                "Not available"
            )


        # Inflation

        if "Inflation" in indicator_data:

            col4.metric(
                f"Inflation",
                format_percentage(
                    indicator_data["Inflation"]
                )
            )

        else:

            col4.metric(
                f"Inflation",
                "Not available"
            )


        # =================================================
        # POPULATION & TRADE
        # =================================================

        st.subheader("Population & Trade")

        trade_col1, trade_col2, trade_col3, trade_col4 = st.columns(4)


        # Population

        if "Population" in indicator_data:

            trade_col1.metric(
                "Population",
                format_population(
                    indicator_data["Population"]
                )
            )

        else:

            trade_col1.metric(
                "Population",
                "Not available"
            )


        # Exports

        if "Exports" in indicator_data:

            trade_col2.metric(
                "Exports",
                format_billions(
                    indicator_data["Exports"]
                )
            )

        else:

            trade_col2.metric(
                "Exports",
                "Not available"
            )


        # Imports

        if "Imports" in indicator_data:

            trade_col3.metric(
                "Imports",
                format_billions(
                    indicator_data["Imports"]
                )
            )

        else:

            trade_col3.metric(
                "Imports",
                "Not available"
            )


        # Trade Balance

        if "Trade Balance" in indicator_data:

            trade_col4.metric(
                "Trade Balance",
                format_billions(
                    indicator_data["Trade Balance"]
                )
            )

        else:

            trade_col4.metric(
                "Trade Balance",
                "Not available"
            )


        # =================================================
        # ECONOMIC STRUCTURE
        # =================================================

        st.subheader("Economic Structure")

        sector_col1, sector_col2, sector_col3 = st.columns(3)


        # Agriculture

        if "Agriculture" in indicator_data:

            sector_col1.metric(
                "Agriculture",
                format_percentage(
                    indicator_data["Agriculture"]
                )
            )

        else:

            sector_col1.metric(
                "Agriculture",
                "Not available"
            )


        # Industry

        if "Industry" in indicator_data:

            sector_col2.metric(
                "Industry",
                format_percentage(
                    indicator_data["Industry"]
                )
            )

        else:

            sector_col2.metric(
                "Industry",
                "Not available"
            )


        # Services

        if "Services" in indicator_data:

            sector_col3.metric(
                "Services",
                format_percentage(
                    indicator_data["Services"]
                )
            )

        else:

            sector_col3.metric(
                "Services",
                "Not available"
            )

    # =====================================================
    # HISTORICAL TRENDS
    # =====================================================

    with charts_tab:

        st.subheader("Historical Period")

        period_col1, period_col2 = st.columns(2)

        with period_col1:
            start_year = st.number_input(
                "Start Year:",
                min_value=1960,
                max_value=2025,
                value=2010,
                step=1,
                key="historical_start_year"
            )

        with period_col2:
            end_year = st.number_input(
                "End Year:",
                min_value=1960,
                max_value=2025,
                value=2024,
                step=1,
                key="historical_end_year"
            )

        if start_year > end_year:
            st.error(
                "Start Year must be earlier than End Year."
            )

        def show_indicator_chart(
            indicator_name,
            country_code
        ):

            data = get_world_bank_data(
                country_code,
                INDICATORS[indicator_name]["code"]
            )

            if not data.empty:

                data = data[
                    (data["Year"] >= start_year)
                    & (data["Year"] <= end_year)
                ]

                if data.empty:

                    st.info(
                        f"No {indicator_name} data available "
                        f"between {start_year} and {end_year}."
                    )

                    return

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

            show_indicator_chart(
                "Population",
                country_code
            )

            show_indicator_chart(
                "Exports",
                country_code
            )

            show_indicator_chart(
                "Imports",
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

            show_indicator_chart(
                "Agriculture",
                country_code
            )

            show_indicator_chart(
                "Industry",
                country_code
            )

            show_indicator_chart(
                "Services",
                country_code
            )


# =========================================================
# COUNTRY COMPARISON
# =========================================================

elif mode == "Country Comparison":

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


        # =================================================
        # COLLECT DATA
        # =================================================

        for country in selected_countries:

            country_code = COUNTRIES[country]

            country_record = {
                "Country": country
            }


            for indicator_name, indicator_info in INDICATORS.items():

                if indicator_info["type"] == "calculated":
                    continue

                data = get_world_bank_data(
                    country_code,
                    indicator_info["code"]
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


            # Trade Balance

            exports_value = country_record.get("Exports")
            imports_value = country_record.get("Imports")

            if (
                exports_value is not None
                and imports_value is not None
            ):

                country_record["Trade Balance"] = (
                    exports_value - imports_value
                )

            else:

                country_record["Trade Balance"] = None


            comparison_data.append(
                country_record
            )


        comparison_df = pd.DataFrame(
            comparison_data
        )


        # =================================================
        # COMPARISON TABLE
        # =================================================

        st.subheader("Economic Indicators")

        formatted_df = comparison_df.copy()


        if "GDP" in formatted_df.columns:

            formatted_df["GDP"] = formatted_df["GDP"].apply(
                lambda x:
                    format_billions(x)
            )


        if "GDP growth" in formatted_df.columns:

            formatted_df["GDP growth"] = formatted_df[
                "GDP growth"
            ].apply(
                lambda x:
                    format_percentage(x)
            )


        if "GDP per capita" in formatted_df.columns:

            formatted_df["GDP per capita"] = formatted_df[
                "GDP per capita"
            ].apply(
                lambda x:
                    format_currency(x)
            )


        if "Inflation" in formatted_df.columns:

            formatted_df["Inflation"] = formatted_df[
                "Inflation"
            ].apply(
                lambda x:
                    format_percentage(x)
            )


        if "Population" in formatted_df.columns:

            formatted_df["Population"] = formatted_df[
                "Population"
            ].apply(
                lambda x:
                    format_population(x)
            )


        for column in [
            "Exports",
            "Imports",
            "Trade Balance"
        ]:

            if column in formatted_df.columns:

                formatted_df[column] = formatted_df[
                    column
                ].apply(
                    lambda x:
                        format_billions(x)
                )


        for column in [
            "Agriculture",
            "Industry",
            "Services"
        ]:

            if column in formatted_df.columns:

                formatted_df[column] = formatted_df[
                    column
                ].apply(
                    lambda x:
                        format_percentage(x)
                )


        st.dataframe(
            formatted_df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # ECONOMIC ANALYSIS
        # =================================================

        st.subheader("Economic Analysis")

        st.caption(
            f"Based on available data for {comparison_year}."
        )


        for indicator in [
            "GDP",
            "GDP per capita",
            "GDP growth",
            "Inflation",
            "Population",
            "Exports",
            "Imports",
            "Trade Balance",
            "Agriculture",
            "Industry",
            "Services"
        ]:

            if indicator not in comparison_df.columns:
                continue

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

                highest_value = highest[indicator]
                lowest_value = lowest[indicator]

                st.write(
                    f"**{indicator}:** "
                    f"{highest['Country']} has the highest value "
                    f"({highest_value:,.2f})."
                )

                st.write(
                    f"Lowest: {lowest['Country']} "
                    f"({lowest_value:,.2f})."
                )

                if lowest_value != 0:

                    relative_difference = (
                        (highest_value - lowest_value)
                        / abs(lowest_value)
                    ) * 100

                    st.write(
                        f"**Relative Difference:** "
                        f"{relative_difference:.2f}%"
                    )

                else:

                    st.write(
                        "**Relative Difference:** "
                        "Cannot be calculated because the lowest value is zero."
                    )

            else:

                st.write(
                    f"**{indicator}:** "
                    f"Not enough data available for comparison."
                )


        # =================================================
        # COMPARISON CHARTS
        # =================================================

        st.subheader("Visual Comparison")

        st.caption(
            f"Comparison of selected countries in {comparison_year}."
        )


        chart_indicators = [
            "GDP",
            "GDP growth",
            "GDP per capita",
            "Inflation",
            "Population",
            "Exports",
            "Imports",
            "Trade Balance",
            "Agriculture",
            "Industry",
            "Services"
        ]


        for indicator in chart_indicators:

            if indicator not in comparison_df.columns:
                continue

            chart_data = comparison_df[
                ["Country", indicator]
            ].dropna()


            if not chart_data.empty:

                chart_data = chart_data.set_index(
                    "Country"
                )

                st.write(
                    f"**{indicator}**"
                )

                st.bar_chart(
                    chart_data[indicator]
                )

            else:

                st.info(
                    f"{indicator} data is not available."
                )

# =========================================================
# REGIONAL ANALYSIS
# =========================================================

elif mode == "Regional Analysis":

    st.header("Arab Regional Analysis")

    st.caption(
        f"Regional comparison of {regional_indicator} in {regional_year}."
    )

    indicator_code = INDICATORS[regional_indicator]["code"]

    regional_data = []

    for country, country_code in COUNTRIES.items():

        data = get_world_bank_data(
            country_code,
            indicator_code
        )

        if not data.empty:

            year_data = data[
                data["Year"] == regional_year
            ]

            if not year_data.empty:

                regional_data.append({
                    "Country": country,
                    regional_indicator: year_data.iloc[0]["Value"]
                })


    regional_df = pd.DataFrame(regional_data)


    if regional_df.empty:

        st.warning(
            "No regional data is available for the selected indicator and year."
        )

    else:

        # =============================================
        # REGIONAL STATISTICS
        # =============================================

        regional_average = regional_df[
            regional_indicator
        ].mean()

        highest = regional_df.loc[
            regional_df[regional_indicator].idxmax()
        ]

        lowest = regional_df.loc[
            regional_df[regional_indicator].idxmin()
        ]


        st.subheader("Regional Overview")

        stat_col1, stat_col2, stat_col3 = st.columns(3)


        stat_col1.metric(
            "Regional Average",
            (
                f"{regional_average:.2f}%"
                if INDICATORS[regional_indicator]["unit"] == "%"
                else format_billions(regional_average)
            )
        )

        stat_col2.metric(
            "Highest",
            highest["Country"]
        )

        stat_col3.metric(
            "Lowest",
            lowest["Country"]
        )


        # =============================================
        # RANKING
        # =============================================

        st.subheader("Country Ranking")

        ranking_df = regional_df.sort_values(
            regional_indicator,
            ascending=False
        ).reset_index(drop=True)

        st.dataframe(
            ranking_df,
            use_container_width=True,
            hide_index=True
        )


        # =============================================
        # VISUAL COMPARISON
        # =============================================

        st.subheader("Regional Comparison")

        chart_data = ranking_df.set_index("Country")

        st.bar_chart(
            chart_data[regional_indicator]
        )

        # =============================================
        # ECONOMIC INSIGHTS
        # =============================================

        st.subheader("Economic Insights")

        if not regional_df.empty:

            highest_value = highest[regional_indicator]
            lowest_value = lowest[regional_indicator]

            st.write(
                f"**Highest:** {highest['Country']} "
                f"has the highest {regional_indicator} "
                f"at {highest_value:,.2f}."
            )

            st.write(
                f"**Lowest:** {lowest['Country']} "
                f"has the lowest {regional_indicator} "
                f"at {lowest_value:,.2f}."
            )

            if lowest_value != 0:

                relative_difference = (
                    (highest_value - lowest_value)
                    / abs(lowest_value)
                ) * 100

                st.write(
                    f"**Relative Difference:** "
                    f"{highest['Country']} is "
                    f"{relative_difference:.2f}% higher than "
                    f"{lowest['Country']}."
                )

            else:

                st.write(
                    "**Relative Difference:** "
                    "Cannot be calculated because the lowest value is zero."
                )

        # =============================================
        # REGIONAL TREND
        # =============================================
        
        st.subheader("Regional Trend")

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:

            regional_start_year = st.number_input(
                "Start Year:",
                min_value=1960,
                max_value=2025,
                value=2010,
                step=1,
                key="regional_start_year"
            )

        with trend_col2:

            regional_end_year = st.number_input(
                "End Year:",
                min_value=1960,
                max_value=2025,
                value=2024,
                step=1,
                key="regional_end_year"
            )

        if regional_start_year > regional_end_year:

            st.error(
                "Start Year must be earlier than End Year."
            )

        st.subheader("Regional Trend")

        trend_records = []

        for year in range(
            regional_start_year,
            regional_end_year + 1
        ):

            year_values = []

            for country, country_code in COUNTRIES.items():

                data = get_world_bank_data(
                    country_code,
                    indicator_code
                )

                if not data.empty:

                    year_data = data[
                        data["Year"] == year
                    ]

                    if not year_data.empty:

                        year_values.append(
                            year_data.iloc[0]["Value"]
                        )

            if year_values:

                trend_records.append({
                    "Year": year,
                    "Regional Average": sum(year_values) / len(year_values)
                })


        trend_df = pd.DataFrame(trend_records)

        if not trend_df.empty:

            trend_df = trend_df.set_index("Year")

            st.line_chart(
                trend_df["Regional Average"]
            )

        else:

            st.info(
                "No regional trend data is available for the selected period."
            )


# =========================================================
# ABOUT
# =========================================================

elif mode == "About ArabScope":

    st.header("What is ArabScope?")

    st.write(
        """
        ArabScope is an interactive economic
        data dashboard designed to explore and compare key
        economic indicators across Arab countries.
        """
    )

    st.subheader("Data Sources")

    st.write(
        """
        The economic data used in this application comes from
        the World Bank Open Data API.
        """
    )

    st.subheader("Methodology")

    st.write(
        """
        ArabScope collects economic indicators from the World Bank
        and allows users to explore individual countries, compare
        multiple Arab countries, and analyze regional economic trends.
        """
    )


    st.subheader("Economic Indicators")

    st.markdown(
        """
        - **GDP:** Total economic output of a country.
        - **GDP Growth:** Annual percentage growth of GDP.
        - **GDP per Capita:** GDP divided by the population.
        - **Inflation:** Annual percentage change in consumer prices.
        - **Population:** Total population.
        - **Exports:** Exports of goods and services.
        - **Imports:** Imports of goods and services.
        - **Trade Balance:** Exports minus imports.
        - **Agriculture:** Agriculture, forestry, and fishing as a percentage of GDP.
        - **Industry:** Industry as a percentage of GDP.
        - **Services:** Services as a percentage of GDP.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Data source: World Bank Open Data"
)