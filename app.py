
import os
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI Pharmacy Inventory Assistant", page_icon="💊", layout="wide")

st.title("💊 AI Pharmacy Inventory Assistant")
st.caption("A practical AI prototype for identifying low-stock medicines and generating reorder priorities.")

st.markdown("""
This prototype combines **inventory rules** with an **AI explanation layer**.
Upload a CSV containing: `Medicine`, `Quantity`, `Minimum_Stock`, and `Unit_Price`.
""")

uploaded = st.file_uploader("Upload inventory CSV", type=["csv"])

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        required = {"Medicine", "Quantity", "Minimum_Stock", "Unit_Price"}
        missing = required - set(df.columns)

        if missing:
            st.error(f"Missing columns: {', '.join(sorted(missing))}")
            st.info("Your CSV should contain Medicine, Quantity, Minimum_Stock, Unit_Price.")
            st.stop()

        for col in ["Quantity", "Minimum_Stock", "Unit_Price"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["Stock_Status"] = df.apply(
            lambda r: "CRITICAL" if r["Quantity"] <= 0
            else ("LOW" if r["Quantity"] < r["Minimum_Stock"] else "OK"),
            axis=1
        )
        df["Suggested_Reorder"] = (df["Minimum_Stock"] * 2 - df["Quantity"]).clip(lower=0)
        df["Estimated_Reorder_Cost"] = df["Suggested_Reorder"] * df["Unit_Price"]

        st.subheader("Inventory overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Medicines", len(df))
        c2.metric("Low / critical", int((df["Stock_Status"] != "OK").sum()))
        c3.metric("Estimated reorder cost", f"KSh {df['Estimated_Reorder_Cost'].sum():,.0f}")

        st.subheader("Reorder priorities")
        priority = df[df["Stock_Status"] != "OK"].copy()
        priority["Priority"] = priority["Stock_Status"].map({"CRITICAL": 1, "LOW": 2})
        priority = priority.sort_values(["Priority", "Quantity"])

        if priority.empty:
            st.success("No medicines are currently below their minimum stock level.")
        else:
            st.dataframe(
                priority[[
                    "Medicine", "Quantity", "Minimum_Stock",
                    "Stock_Status", "Suggested_Reorder",
                    "Unit_Price", "Estimated_Reorder_Cost"
                ]],
                use_container_width=True,
                hide_index=True
            )

        st.subheader("AI explanation")
        api_key = st.text_input(
            "Optional Gemini API key",
            type="password",
            help="If supplied, the app uses Gemini to explain the reorder priorities. Leave blank to use the built-in rule-based summary."
        )

        if st.button("Generate inventory recommendation", type="primary"):
            if priority.empty:
                st.info("There are no low-stock items requiring a recommendation.")
            elif api_key:
                try:
                    from google import genai
                    client = genai.Client(api_key=api_key)

                    records = priority[[
                        "Medicine", "Quantity", "Minimum_Stock",
                        "Stock_Status", "Suggested_Reorder"
                    ]].to_dict(orient="records")

                    prompt = f"""
You are an inventory assistant. Review this pharmacy inventory data:
{json.dumps(records, indent=2)}

Give a concise operational recommendation. Identify the most urgent items,
explain why they are urgent, and suggest what the pharmacist/store manager
should check before ordering. Do not diagnose patients or recommend treatment.
"""
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.write(response.text)
                except Exception as e:
                    st.warning("The AI service could not be reached, so the app generated a local recommendation instead.")
                    st.write("Check the Gemini API key and internet connection.")
            else:
                critical = priority[priority["Stock_Status"] == "CRITICAL"]["Medicine"].tolist()
                low = priority[priority["Stock_Status"] == "LOW"]["Medicine"].tolist()

                if critical:
                    st.error("Immediate attention: " + ", ".join(critical))
                if low:
                    st.warning("Reorder soon: " + ", ".join(low))

                st.write(
                    "The assistant prioritizes medicines with zero stock first, "
                    "followed by medicines below their minimum stock level. "
                    "The suggested reorder quantity targets approximately twice "
                    "the minimum stock level."
                )

        with st.expander("How this project uses AI"):
            st.write(
                "The core inventory calculations are deterministic rules so that "
                "stock thresholds remain transparent. When a Gemini API key is "
                "provided, Gemini converts the structured inventory findings into "
                "a concise human-readable operational recommendation."
            )

    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
else:
    st.info("Upload an inventory CSV to begin.")

st.divider()
st.caption("Prototype for portfolio / AI Showcase demonstration. Not a substitute for pharmacy inventory policies or professional judgment.")
