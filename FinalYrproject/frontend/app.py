import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# =========================
# CONFIGURATION
# =========================
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="INFY Stock Predictor",
    layout="wide"
)

# =========================
# TITLE
# =========================
st.title("📈 Infosys (INFY) Stock Price Prediction")
st.markdown(
    "Visualize historical stock prices and forecast future values using a deep learning model."
)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Forecast Settings")

days_to_predict = st.sidebar.slider(
    "Days to Predict",
    min_value=1,
    max_value=30,
    value=7
)

predict_btn = st.sidebar.button("Generate Prediction")

# =========================
# BACKEND STATUS
# =========================
try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if health.status_code == 200:
        st.sidebar.success("Backend Connected 🟢")
    else:
        st.sidebar.error("Backend Error 🔴")
except:
    st.sidebar.error("Backend Offline 🔴")

# =========================
# MAIN LAYOUT
# =========================
col1, col2 = st.columns([3, 1])

# =========================
# LEFT COLUMN – CHART
# =========================
with col1:
    st.subheader("Stock Price History & Forecast")

    with st.spinner("Loading historical data..."):
        try:
            hist_resp = requests.get(f"{BACKEND_URL}/history?period=1y")

            if hist_resp.status_code == 200:
                hist_data = hist_resp.json()["data"]
                df_hist = pd.DataFrame(hist_data)

                # Ensure datetime
                df_hist["Date"] = pd.to_datetime(df_hist["Date"])

                # 🔥 CREATE MONTH COLUMN FOR X-AXIS
                df_hist["Month"] = df_hist["Date"].dt.strftime("%b-%Y")

                fig = go.Figure()

                # =========================
                # HISTORICAL PRICES (MONTH VIEW)
                # =========================
                fig.add_trace(
                    go.Scatter(
                        x=df_hist["Month"],   # ✅ MONTH X-AXIS
                        y=df_hist["Close"],
                        mode="lines",
                        name="Historical Close"
                    )
                )

                # =========================
                # FORECAST (MONTH VIEW)
                # =========================
                if predict_btn:
                    with st.spinner(f"Predicting next {days_to_predict} days..."):
                        pred_resp = requests.post(
                            f"{BACKEND_URL}/predict",
                            json={"days": days_to_predict}
                        )

                        if pred_resp.status_code == 200:
                            pred_data = pred_resp.json()
                            pred_dates = pd.to_datetime(pred_data["dates"])
                            pred_vals = pred_data["predictions"]

                            pred_months = pred_dates.strftime("%b-%Y")

                            fig.add_trace(
                                go.Scatter(
                                    x=pred_months,   # ✅ MONTH X-AXIS
                                    y=pred_vals,
                                    mode="lines+markers",
                                    name="Forecast",
                                    line=dict(color="red", dash="dash")
                                )
                            )

                            st.success(f"Prediction generated for {days_to_predict} days!")
                        else:
                            st.error("Prediction failed.")

                # =========================
                # FORCE MONTH AXIS
                # =========================
                fig.update_layout(
                    title="INFY Stock Price Trend (Monthly View)",
                    xaxis_title="Month",
                    yaxis_title="Price (INR)",
                    xaxis=dict(type="category"),  # 🔥 KEY LINE
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error("Failed to load historical data.")

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# RIGHT COLUMN – TABLES
# =========================
with col2:
    st.subheader("Recent Data")

    if "df_hist" in locals():
        st.dataframe(
            df_hist[["Date", "Close", "Volume"]].tail(10),
            use_container_width=True
        )

    if predict_btn and "pred_vals" in locals():
        st.subheader("Forecast Values")

        df_pred = pd.DataFrame({
            "Date": pred_dates,
            "Predicted Price (INR)": pred_vals
        })

        st.dataframe(df_pred, use_container_width=True)

        csv = df_pred.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Predictions as CSV",
            data=csv,
            file_name="infy_predictions.csv",
            mime="text/csv"
        )
