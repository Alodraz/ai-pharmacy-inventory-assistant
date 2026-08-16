
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
        c3.metric("Estimated reorder cost", f"${df['Estimated_Reorder_Cost'].sum():,.2f}")
        st.subheader("Reorder priorities")
        priority = df[df["Stock_Status"] != "OK"].copy()
        priority["Priority"] = priority["Stock_Status"].map({"CRITICAL": 1, "LOW": 2})
        priority = priority.sort_values(["Priority", "Quantity"])

        if priority.empty:
            st.success("No medicines are currently below their minimum stock level.")
        else:
            display_df = priority[
            [
                "Medicine", "Quantity", "Minimum_Stock",
                "Stock_Status", "Suggested_Reorder",
                "Unit_Price", "Estimated_Reorder_Cost"
            ]
        ].style.format({
            "Unit_Price": "${:,.2f}",
            "Estimated_Reorder_Cost": "${:,.2f}"
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("AI explanation")
        api_key = st.text_input(
            "Optional Gemini API key",
            type="password",
            help="If supplied, the app uses Gemini to explain the reorder priorities. Leave blank to use the built-in rule-based summary."
        )

        if st.bif st.button("Generate inventory recommendation", type="primary"):
    if priority.empty:
        st.info("There are no low-stock items requiring a recommendation.")

    elif api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)

            records = priority[
                [
                    "Medicine",
                    "Quantity",
                    "Minimum_Stock",
                    "Stock_Status",
                    "Suggested_Reorder",
                    "Unit_Price",
                    "Estimated_Reorder_Cost",
                ]
            ].to_dict(orient="records")

            prompt = f"""
You are a pharmacy inventory assistant.

Review the following pharmacy inventory data:

{json.dumps(records, indent=2)}

Give a concise operational inventory recommendation.

For every medicine requiring action:
1. State the medicine name.
2. State the current quantity.
3. State the minimum stock level.
4. State whether it is CRITICAL or LOW.
5. State the suggested reorder quantity.
6. State the estimated reorder cost.

Prioritize CRITICAL items first, followed by LOW items.

Do not diagnose patients or recommend treatment.
Focus only on inventory management and purchasing priorities.
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            st.markdown("### AI Inventory Recommendation")
            st.write(response.text)

        except Exception:
            st.warning(
                "The AI service could not be reached, so the app generated "
                "a local inventory recommendation instead."
            )

            st.markdown("### Inventory Recommendation")

            for _, row in priority.iterrows():
                if row["Stock_Status"] == "CRITICAL":
                    st.error(
                        f"*{row['Medicine']} — CRITICAL*\n\n"
                        f"Current stock: {int(row['Quantity'])} | "
                        f"Minimum stock: {int(row['Minimum_Stock'])}\n\n"
                        f"Suggested reorder: *{int(row['Suggested_Reorder'])} units*\n\n"
                        f"Estimated reorder cost: "
                        f"*${row['Estimated_Reorder_Cost']:,.2f}*"
                    )
                else:
                    st.warning(
                        f"*{row['Medicine']} — LOW STOCK*\n\n"
                        f"Current stock: {int(row['Quantity'])} | "
                        f"Minimum stock: {int(row['Minimum_Stock'])}\n\n"
                        f"Suggested reorder: *{int(row['Suggested_Reorder'])} units*\n\n"
                        f"Estimated reorder cost: "
                        f"*${row['Estimated_Reorder_Cost']:,.2f}*"
                    )

    else:
        st.markdown("### Inventory Recommendation")

        for _, row in priority.iterrows():
            if row["Stock_Status"] == "CRITICAL":
                st.error(
                    f"*{row['Medicine']} — CRITICAL*\n\n"
                    f"Current stock: {int(row['Quantity'])} | "
                    f"Minimum stock: {int(row['Minimum_Stock'])}\n\n"
                    f"Suggested reorder: *{int(row['Suggested_Reorder'])} units*\n\n"
                    f"Estimated reorder cost: "
                    f"*${row['Estimated_Reorder_Cost']:,.2f}*"
                )
            else:
                st.warning(
                    f"*{row['Medicine']} — LOW STOCK*\n\n"
                    f"Current stock: {int(row['Quantity'])} | "
                    f"Minimum stock: {int(row['Minimum_Stock'])}\n\n"
                    f"Suggested reorder: *{int(row['Suggested_Reorder'])} units*\n\n"
                    f"Estimated reorder cost: "
                    f"*${row['Estimated_Reorder_Cost']:,.2f}*"
                )
