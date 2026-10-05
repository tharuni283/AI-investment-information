import streamlit as st
import ollama
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pypdf import PdfReader

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Investment Information Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# INVESTMENT DATA
# ---------------------------------------------------------

INVESTMENTS = {
    "🏦 Bank / Fixed Deposits": {
        "what": "Bank fixed deposits allow you to deposit money with a bank for a chosen period and earn interest.",
        "why": "People often consider fixed deposits when they want relatively predictable returns and capital preservation.",
        "benefits": [
            "Generally simple to understand",
            "Predictable interest structure",
            "Useful for short or medium-term goals",
            "Usually easier to access than many long-term investments"
        ],
        "risks": [
            "Returns may be lower than growth-oriented investments",
            "Inflation can reduce real purchasing power",
            "Early withdrawal may have conditions or penalties"
        ],
        "liquidity": "Medium",
        "risk": "Low",
        "horizon": "Short to medium term",
        "check": [
            "Interest rate",
            "Tenure",
            "Premature withdrawal conditions",
            "Tax treatment",
            "Deposit insurance rules"
        ],
        "assumed_return": 6.5
    },

    "🪙 Gold": {
        "what": "Gold is a traditional asset that can be held physically or through certain financial products.",
        "why": "Investors may consider gold for diversification and as an asset that can behave differently from some other investments.",
        "benefits": [
            "Can diversify a portfolio",
            "Widely recognized store of value",
            "Can be useful as part of a diversified strategy",
            "Available through different investment formats"
        ],
        "risks": [
            "Market prices can fluctuate",
            "Physical gold can involve storage and security costs",
            "Returns are not guaranteed"
        ],
        "liquidity": "High",
        "risk": "Medium",
        "horizon": "Medium to long term",
        "check": [
            "Purity",
            "Buy/sell spread",
            "Storage costs for physical gold",
            "Product fees",
            "Market price"
        ],
        "assumed_return": 7.0
    },

    "🏠 Land / Real Estate": {
        "what": "Real estate investing involves owning property or land with the expectation that its value or income potential may increase over time.",
        "why": "People may consider real estate for long-term wealth creation, rental income, or diversification.",
        "benefits": [
            "Potential long-term appreciation",
            "Possible rental income",
            "Physical asset",
            "Can diversify wealth"
        ],
        "risks": [
            "Large initial capital requirement",
            "Lower liquidity than many financial assets",
            "Property prices can decline",
            "Maintenance, legal and transaction costs may apply"
        ],
        "liquidity": "Low",
        "risk": "Medium to High",
        "horizon": "Long term",
        "check": [
            "Location",
            "Title and legal documents",
            "Market demand",
            "Taxes and transaction costs",
            "Maintenance requirements"
        ],
        "assumed_return": 8.0
    },

    "📈 Stocks": {
        "what": "Stocks represent ownership interests in companies. Their market prices can rise or fall significantly.",
        "why": "Investors may consider stocks for long-term growth and participation in company performance.",
        "benefits": [
            "Potential for long-term capital growth",
            "High liquidity for listed stocks",
            "Wide range of companies and sectors",
            "Can support portfolio diversification"
        ],
        "risks": [
            "Prices can fluctuate significantly",
            "Potential for loss of capital",
            "Company-specific risks",
            "Requires research and monitoring"
        ],
        "liquidity": "High",
        "risk": "High",
        "horizon": "Long term",
        "check": [
            "Company fundamentals",
            "Valuation",
            "Business risks",
            "Diversification",
            "Investment horizon"
        ],
        "assumed_return": 11.0
    },

    "📊 Mutual Funds": {
        "what": "Mutual funds pool money from investors and invest it across assets according to the fund's strategy.",
        "why": "They can provide diversification and professional portfolio management.",
        "benefits": [
            "Diversification",
            "Professional management",
            "Different fund categories available",
            "Can support systematic investing"
        ],
        "risks": [
            "Market-linked returns can fluctuate",
            "Management and other expenses may apply",
            "No guaranteed return for market-linked funds",
            "Fund performance can vary"
        ],
        "liquidity": "Medium to High",
        "risk": "Medium to High",
        "horizon": "Medium to long term",
        "check": [
            "Fund objective",
            "Risk level",
            "Expense ratio",
            "Past performance context",
            "Portfolio composition"
        ],
        "assumed_return": 10.0
    },

    "🏛️ Government Bonds": {
        "what": "Government bonds are debt instruments issued by governments to raise funds.",
        "why": "Investors may consider them when looking for relatively lower-risk fixed-income exposure.",
        "benefits": [
            "Generally considered lower credit risk for sovereign issuers",
            "Can provide income",
            "Useful for portfolio diversification",
            "Can complement growth-oriented investments"
        ],
        "risks": [
            "Interest-rate risk",
            "Inflation can reduce real returns",
            "Market value can change before maturity",
            "Returns depend on the specific bond"
        ],
        "liquidity": "Medium",
        "risk": "Low to Medium",
        "horizon": "Medium to long term",
        "check": [
            "Maturity",
            "Coupon or yield",
            "Interest-rate environment",
            "Liquidity",
            "Tax treatment"
        ],
        "assumed_return": 7.0
    },

    "🛡️ Insurance-related Protection": {
        "what": "Insurance is primarily designed to provide financial protection against specified risks. Some products may also have savings or investment-linked features.",
        "why": "People may consider insurance to protect dependents, income, health or assets from specified financial risks.",
        "benefits": [
            "Financial protection against covered risks",
            "Can support family financial planning",
            "May protect income or assets depending on the product",
            "Some products may combine protection with savings features"
        ],
        "risks": [
            "Premiums are an ongoing financial commitment",
            "Policy terms and exclusions must be understood",
            "Some products may have limited liquidity",
            "Investment-linked products can carry market risk"
        ],
        "liquidity": "Low to Medium",
        "risk": "Low to High depending on product",
        "horizon": "Medium to long term",
        "check": [
            "Coverage",
            "Exclusions",
            "Premium",
            "Policy term",
            "Claim conditions",
            "Charges"
        ],
        "assumed_return": 5.0
    },

    "👵 Retirement-oriented Options": {
        "what": "Retirement-oriented investing focuses on building financial resources for future retirement needs.",
        "why": "Long-term retirement planning can help prepare for expenses after regular employment income reduces or stops.",
        "benefits": [
            "Encourages long-term saving",
            "Supports retirement goals",
            "Allows time for compounding",
            "Can combine different asset classes"
        ],
        "risks": [
            "Long investment horizon",
            "Inflation can affect future purchasing power",
            "Market-linked options can fluctuate",
            "Early withdrawals may have restrictions"
        ],
        "liquidity": "Low to Medium",
        "risk": "Depends on underlying assets",
        "horizon": "Long term",
        "check": [
            "Retirement age",
            "Expected expenses",
            "Inflation",
            "Asset allocation",
            "Withdrawal rules"
        ],
        "assumed_return": 9.0
    },

    "💰 Other Investment Categories": {
        "what": "Other investment categories can include different financial or alternative assets depending on an investor's objectives and risk tolerance.",
        "why": "Exploring multiple asset classes can help investors understand diversification and different risk-return characteristics.",
        "benefits": [
            "More diversification possibilities",
            "Different return and risk characteristics",
            "Can be matched to different financial goals"
        ],
        "risks": [
            "Some alternatives can be complex",
            "Liquidity may be limited",
            "Fees can vary",
            "Risk can differ significantly between products"
        ],
        "liquidity": "Varies",
        "risk": "Varies",
        "horizon": "Varies",
        "check": [
            "Product structure",
            "Risk",
            "Liquidity",
            "Fees",
            "Regulatory framework"
        ],
        "assumed_return": 8.0
    }
}

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_investment" not in st.session_state:
    st.session_state.selected_investment = None

if "amount" not in st.session_state:
    st.session_state.amount = 100000.0

if "monthly_investment" not in st.session_state:
    st.session_state.monthly_investment = 5000.0

if "period" not in st.session_state:
    st.session_state.period = 10

if "goal" not in st.session_state:
    st.session_state.goal = "Wealth creation"

if "risk_profile" not in st.session_state:
    st.session_state.risk_profile = None

if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None

if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def go_to(page):
    st.session_state.page = page


def calculate_future_value(principal, annual_rate, years):
    rate = annual_rate / 100
    return principal * ((1 + rate) ** years)


def calculate_monthly_future_value(monthly, annual_rate, years):
    monthly_rate = annual_rate / 100 / 12
    months = years * 12

    if monthly_rate == 0:
        return monthly * months

    return monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)


def ask_llama(question):
    question = question.strip()

    if not question:
        return "Please enter a question."

    prompt = f"""
You are Llama 3.2 working as an AI Investment Information Assistant.

Your job is to EDUCATE users about investment concepts.

Important rules:
- Do not promise profits.
- Do not guarantee investment returns.
- Do not tell the user to buy a specific financial product.
- Explain concepts in simple language.
- Clearly distinguish investment information from personalized financial advice.
- If a question is outside investment and financial planning, answer briefly and safely.
- Actual returns depend on market conditions and individual circumstances.

"""

    if st.session_state.pdf_context:
        prompt += f"""
Additional information from an uploaded PDF:

{st.session_state.pdf_context[:12000]}

"""

    prompt += f"""
User question:
{question}

Give a clear, useful answer.
"""

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return (
            "I could not connect to Llama 3.2 right now. "
            "Please make sure Ollama is running and the llama3.2 model is installed.\n\n"
            f"Technical detail: {e}"
        )


def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        return f"Could not read the PDF: {e}"


def calculate_risk_profile(duration, loss_comfort, goal, safety_preference):

    score = 0

    if duration == "Less than 3 years":
        score += 1
    elif duration == "3–7 years":
        score += 2
    else:
        score += 3

    if loss_comfort == "Very uncomfortable":
        score += 1
    elif loss_comfort == "Somewhat comfortable":
        score += 2
    else:
        score += 3

    if goal in ["Capital preservation", "Emergency / short-term need"]:
        score += 1
    elif goal == "Balanced growth":
        score += 2
    else:
        score += 3

    if safety_preference == "Safety":
        score += 1
    elif safety_preference == "Balance":
        score += 2
    else:
        score += 3

    if score <= 6:
        return "Conservative", "You appear to prefer stability and lower volatility."
    elif score <= 9:
        return "Moderate", "You appear to prefer a balance between stability and growth."
    else:
        return "Growth-oriented", "You appear more comfortable accepting higher volatility for potential long-term growth."


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## 🤖 Ask Llama 3.2")

    st.caption(
        "Ask questions about investments, risk, liquidity, diversification, "
        "financial planning and related concepts."
    )

    sidebar_question = st.text_area(
        "Your question",
        placeholder="Example: What is the difference between an FD and a mutual fund?",
        height=120
    )

    if st.button("Ask AI", width="stretch"):

        if sidebar_question.strip():

            with st.spinner("Llama 3.2 is thinking..."):
                st.session_state.ai_answer = ask_llama(sidebar_question)

        else:
            st.warning("Please enter a question.")

    if st.session_state.ai_answer:

        st.markdown("---")
        st.markdown("### 💡 Llama's Answer")
        st.write(st.session_state.ai_answer)

    st.markdown("---")

    st.markdown("### 📄 Optional PDF")

    uploaded_pdf = st.file_uploader(
        "Upload an investment-related PDF",
        type=["pdf"]
    )

    if uploaded_pdf:

        with st.spinner("Reading PDF..."):
            pdf_text = extract_pdf_text(uploaded_pdf)

        if pdf_text:

            st.session_state.pdf_context = pdf_text

            st.success("PDF information loaded.")

        else:
            st.warning("No readable text was found in the PDF.")

    st.markdown("---")

    if st.button("🏠 Home", width="stretch"):
        go_to("home")

    if st.button("📊 Explore Investments", width="stretch"):
        go_to("explore")

    if st.button("⚖️ Compare Investments", width="stretch"):
        go_to("compare")

    if st.button("🎯 Risk Profile", width="stretch"):
        go_to("risk")

    if st.button("📄 Final Summary", width="stretch"):
        go_to("summary")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .info-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">🤖 AI Investment Information Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Explore investments • Understand risk • Compare options • Learn with AI</div>',
    unsafe_allow_html=True
)


# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.page == "home":

    st.header("Welcome to Your Investment Information Assistant")

    st.write(
        """
        Investment planning is the process of understanding different ways
        to save and invest money according to financial goals, time horizon,
        risk tolerance and liquidity needs.
        """
    )

    st.write(
        """
        This application helps you explore different investment sectors,
        understand their advantages and risks, calculate educational
        illustrations, compare options and ask questions to Llama 3.2.
        """
    )

    st.info(
        "💡 The calculations in this application are educational illustrations. "
        "Actual investment returns are not guaranteed."
    )

    st.markdown("### 🌟 What can you explore?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊 Explore")
        st.write(
            "Learn about Gold, Stocks, Mutual Funds, Fixed Deposits, "
            "Real Estate, Bonds, Insurance-related protection and more."
        )

    with col2:
        st.markdown("### 🧮 Calculate")
        st.write(
            "Enter an amount, investment period and assumptions to see "
            "an illustrative future value."
        )

    with col3:
        st.markdown("### 🤖 Ask AI")
        st.write(
            "Ask Llama 3.2 questions about investment concepts in simple language."
        )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Explore Investments", width="stretch"):
            go_to("explore")
            st.rerun()

    with col2:
        if st.button("⚖️ Compare Investments", width="stretch"):
            go_to("compare")
            st.rerun()

    with col3:
        if st.button("🤖 Ask AI", width="stretch"):
            st.info(
                "Use the Ask Llama 3.2 section in the left sidebar to ask your question."
            )


# =========================================================
# EXPLORE PAGE
# =========================================================

elif st.session_state.page == "explore":

    st.header("📊 Explore Investment Sectors")

    selected = st.selectbox(
        "Choose an investment sector",
        list(INVESTMENTS.keys())
    )

    st.session_state.selected_investment = selected

    data = INVESTMENTS[selected]

    st.markdown(f"## {selected}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Risk Level", data["risk"])

    with col2:
        st.metric("Liquidity", data["liquidity"])

    with col3:
        st.metric("Typical Horizon", data["horizon"])

    st.markdown("---")

    st.subheader("What is it?")

    st.write(data["what"])

    st.subheader("Why do people consider it?")

    st.write(data["why"])

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Benefits")

        for item in data["benefits"]:
            st.write(f"• {item}")

    with col2:

        st.subheader("⚠️ Disadvantages / Risks")

        for item in data["risks"]:
            st.write(f"• {item}")

    st.subheader("🔎 Important things to check")

    for item in data["check"]:
        st.write(f"• {item}")

    st.markdown("---")

    st.subheader("🧮 Enter Investment Details")

    amount = st.number_input(
        "One-time investment amount",
        min_value=0.0,
        value=float(st.session_state.amount),
        step=1000.0
    )

    monthly = st.number_input(
        "Monthly investment",
        min_value=0.0,
        value=float(st.session_state.monthly_investment),
        step=500.0
    )

    period = st.selectbox(
        "Investment period",
        [1, 2, 5, 10, 20, 30, 40],
        index=[1, 2, 5, 10, 20, 30, 40].index(
            st.session_state.period
        )
    )

    goal = st.selectbox(
        "Main financial goal",
        [
            "Wealth creation",
            "Capital preservation",
            "Retirement planning",
            "Education planning",
            "Emergency / short-term need",
            "Diversification"
        ]
    )

    st.session_state.amount = amount
    st.session_state.monthly_investment = monthly
    st.session_state.period = period
    st.session_state.goal = goal

    st.markdown("---")

    if st.button("📈 Calculate Illustrative Outcome", width="stretch"):

        rate = data["assumed_return"]

        one_time_value = calculate_future_value(
            amount,
            rate,
            period
        )

        monthly_value = calculate_monthly_future_value(
            monthly,
            rate,
            period
        )

        total_invested = amount + (monthly * period * 12)

        future_value = one_time_value + monthly_value

        gain = future_value - total_invested

        st.subheader("📊 Illustrative Result")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Amount Invested",
                f"₹{total_invested:,.0f}"
            )

        with col2:
            st.metric(
                "Illustrative Future Value",
                f"₹{future_value:,.0f}"
            )

        with col3:
            st.metric(
                "Illustrative Gain / Loss",
                f"₹{gain:,.0f}"
            )

        st.caption(
            f"Illustration uses an assumed annual return of {rate:.1f}%. "
            "Actual returns are not guaranteed."
        )


# =========================================================
# SCENARIO ANALYSIS
# =========================================================

elif st.session_state.page == "scenario":

    st.header("📈 Scenario Analysis")

    selected = st.session_state.selected_investment

    if not selected:
        st.warning("Please select an investment first.")
        st.button(
            "Go to Explore",
            on_click=lambda: go_to("explore")
        )
    else:

        data = INVESTMENTS[selected]

        st.write(
            f"Scenario analysis for **{selected}** using educational assumptions."
        )

        amount = st.number_input(
            "Investment amount",
            min_value=0.0,
            value=float(st.session_state.amount),
            step=1000.0
        )

        years = st.number_input(
            "Investment period in years",
            min_value=1,
            max_value=50,
            value=int(st.session_state.period)
        )

        base = data["assumed_return"]

        scenarios = {
            "Conservative": max(1.0, base - 3),
            "Moderate": base,
            "Higher-growth": base + 3
        }

        results = []

        for name, rate in scenarios.items():

            value = calculate_future_value(
                amount,
                rate,
                years
            )

            results.append(
                {
                    "Scenario": name,
                    "Assumed Annual Return": rate,
                    "Illustrative Future Value": value
                }
            )

        df = pd.DataFrame(results)

        st.dataframe(
            df,
            width="stretch"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["Scenario"],
                y=df["Illustrative Future Value"],
                text=[
                    f"₹{x:,.0f}"
                    for x in df["Illustrative Future Value"]
                ],
                textposition="auto"
            )
        )

        fig.update_layout(
            title="Illustrative Scenario Comparison",
            xaxis_title="Scenario",
            yaxis_title="Illustrative Future Value"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.warning(
            "These scenarios use assumptions for educational comparison. "
            "They are not predictions or guaranteed returns."
        )


# =========================================================
# RISK PROFILE
# =========================================================

elif st.session_state.page == "risk":

    st.header("🎯 Educational Risk Profile")

    st.write(
        """
        Answer the following questions to understand which general
        investment style may be more consistent with your preferences.
        """
    )

    duration = st.radio(
        "How long can you keep your investment invested?",
        [
            "Less than 3 years",
            "3–7 years",
            "More than 7 years"
        ]
    )

    loss_comfort = st.radio(
        "How comfortable are you with temporary losses?",
        [
            "Very uncomfortable",
            "Somewhat comfortable",
            "Comfortable with significant fluctuations"
        ]
    )

    goal = st.radio(
        "What is your main goal?",
        [
            "Capital preservation",
            "Balanced growth",
            "Long-term wealth creation",
            "Emergency / short-term need"
        ]
    )

    safety_preference = st.radio(
        "Which do you prefer?",
        [
            "Safety",
            "Balance",
            "Higher growth potential"
        ]
    )

    if st.button("🎯 Calculate Educational Risk Profile", width="stretch"):

        profile, description = calculate_risk_profile(
            duration,
            loss_comfort,
            goal,
            safety_preference
        )

        st.session_state.risk_profile = profile

        st.success(
            f"Your educational risk profile: **{profile}**"
        )

        st.write(description)

        if profile == "Conservative":

            st.info(
                "You may prefer to learn more about lower-volatility "
                "and capital-preservation-oriented options."
            )

        elif profile == "Moderate":

            st.info(
                "You may prefer learning about a balance of growth "
                "and stability across different asset classes."
            )

        else:

            st.info(
                "You may be comfortable learning about higher-volatility "
                "assets when the investment horizon is long enough."
            )

        st.warning(
            "This is an educational risk profile, not personalized financial advice."
        )


# =========================================================
# COMPARE PAGE
# =========================================================

elif st.session_state.page == "compare":

    st.header("⚖️ Compare Investments")

    options = list(INVESTMENTS.keys())

    col1, col2 = st.columns(2)

    with col1:

        first = st.selectbox(
            "First investment",
            options,
            index=0
        )

    with col2:

        second = st.selectbox(
            "Second investment",
            options,
            index=1
        )

    first_data = INVESTMENTS[first]
    second_data = INVESTMENTS[second]

    comparison = pd.DataFrame(
        {
            "Factor": [
                "Risk",
                "Liquidity",
                "Investment Horizon",
                "Illustrative Assumed Return",
                "Benefits",
                "Risks"
            ],
            first: [
                first_data["risk"],
                first_data["liquidity"],
                first_data["horizon"],
                f'{first_data["assumed_return"]:.1f}%',
                " • ".join(first_data["benefits"]),
                " • ".join(first_data["risks"])
            ],
            second: [
                second_data["risk"],
                second_data["liquidity"],
                second_data["horizon"],
                f'{second_data["assumed_return"]:.1f}%',
                " • ".join(second_data["benefits"]),
                " • ".join(second_data["risks"])
            ]
        }
    )

    st.dataframe(
        comparison,
        width="stretch",
        hide_index=True
    )

    st.markdown("---")

    st.subheader("📊 Educational Return Assumption Comparison")

    chart_data = pd.DataFrame(
        {
            "Investment": [first, second],
            "Assumed Return": [
                first_data["assumed_return"],
                second_data["assumed_return"]
            ]
        }
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=chart_data["Investment"],
            y=chart_data["Assumed Return"],
            text=[
                f"{x:.1f}%"
                for x in chart_data["Assumed Return"]
            ],
            textposition="auto"
        )
    )

    fig.update_layout(
        yaxis_title="Assumed Annual Return (%)",
        title="Illustrative Assumptions — Not Predictions"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.warning(
        "A higher assumed return does not mean a higher guaranteed return. "
        "Investment risk, liquidity, costs and time horizon should also be considered."
    )


# =========================================================
# SUMMARY PAGE
# =========================================================

elif st.session_state.page == "summary":

    st.header("📄 Final Investment Information Summary")

    selected = st.session_state.selected_investment

    if selected:

        data = INVESTMENTS[selected]

        st.subheader("Selected Investment")

        st.write(selected)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Amount",
                f"₹{st.session_state.amount:,.0f}"
            )

        with col2:
            st.metric(
                "Period",
                f"{st.session_state.period} years"
            )

        with col3:
            st.metric(
                "Educational Risk Profile",
                st.session_state.risk_profile or "Not calculated"
            )

        st.markdown("---")

        st.subheader("🎯 Financial Goal")

        st.write(st.session_state.goal)

        st.subheader("📊 Investment Information")

        st.write(data["what"])

        st.markdown("### Benefits")

        for item in data["benefits"]:
            st.write(f"• {item}")

        st.markdown("### Risks")

        for item in data["risks"]:
            st.write(f"• {item}")

        st.markdown("### Liquidity")

        st.write(data["liquidity"])

        st.markdown("### Suitable Horizon")

        st.write(data["horizon"])

        if st.session_state.ai_answer:

            st.markdown("---")

            st.subheader("🤖 Recent AI Explanation")

            st.write(st.session_state.ai_answer)

        st.markdown("---")

        st.info(
            "Actual investment outcomes depend on market conditions, "
            "product characteristics, costs, taxes and individual circumstances."
        )

        if st.button("🔄 Compare Again", width="stretch"):

            go_to("compare")
            st.rerun()

        if st.button("🤖 Ask AI", width="stretch"):

            st.info(
                "Use the Ask Llama 3.2 box in the left sidebar."
            )

        if st.button("🏠 Return Home", width="stretch"):

            go_to("home")
            st.rerun()

    else:

        st.warning(
            "You have not selected an investment yet."
        )

        if st.button("📊 Explore Investments", width="stretch"):

            go_to("explore")
            st.rerun()


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "🤖 AI Investment Information Assistant | "
    "Powered by Python + Streamlit + Llama 3.2"
)