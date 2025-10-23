import streamlit as st
import pandas as pd
import io
import zipfile

st.title("🏗️ Door Delivery Planner")

st.write("Upload your door data Excel file and configure weekly delivery details.")

uploaded_file = st.file_uploader("Upload door_data.xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Preview of uploaded data")
    st.dataframe(df.head())

    num_towers = st.number_input("Number of Towers", min_value=1, step=1)
    num_levels = []
    for i in range(int(num_towers)):
        num_levels.append(st.number_input(f"Levels in Tower {i+1}", min_value=1, step=1))

    num_doors = st.number_input("Number of Door Types", min_value=1, step=1)
    door_types = [f"D{i}" for i in range(1, int(num_doors)+1)]

    num_weeks = st.number_input("Number of Weeks", min_value=1, step=1)
    weekly_counts = []
    for i in range(int(num_weeks)):
        weekly_counts.append(st.number_input(f"Doors in Week {i+1}", min_value=1, step=1))

    if st.button("Generate Weekly Plans"):
        rows = []
        for _, row in df.iterrows():
            for d_type in door_types:
                count = int(row.get(d_type, 0))
                for _ in range(count):
                    rows.append({
                        "Tower": row["Tower"],
                        "Level": row["Level"],
                        "Room": row["Room"],
                        "DoorType": d_type
                    })

        all_doors = pd.DataFrame(rows)
        all_doors = all_doors.sort_values(by=["Tower", "Level", "Room"])

        week_limits = [sum(weekly_counts[:i+1]) for i in range(len(weekly_counts))]

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zipf:
            start = 0
            for week, limit in enumerate(week_limits, start=1):
                end = min(limit, len(all_doors))
                week_df = all_doors.iloc[start:end]
                with io.BytesIO() as tmp:
                    week_df.to_excel(tmp, index=False)
                    zipf.writestr(f"Week_{week}.xlsx", tmp.getvalue())
                start = end
        buffer.seek(0)

        st.success("✅ Weekly plans generated successfully!")
        st.download_button(
            label="📦 Download ZIP file",
            data=buffer,
            file_name="Weekly_Plans.zip",
            mime="application/zip"
        )
