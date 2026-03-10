import os
import pandas as pd
import fitdecode

WORKOUT_DIR = "workouts"

records = []
summaries = []

for file in os.listdir(WORKOUT_DIR):
    if not file.endswith(".fit"):
        continue

    path = os.path.join(WORKOUT_DIR, file)
    print("Reading:", file)

    try:
        with fitdecode.FitReader(path) as fit:

            for frame in fit:

                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue

                # ---------- RECORD ----------
                if frame.name == "record":

                    data = {
                        "file": file,
                        "timestamp": None,
                        "distance_m": None,
                        "heart_rate": None,
                        "altitude": None,
                        "speed_mps": None
                    }

                    for field in frame.fields:

                        if field.name == "timestamp":
                            data["timestamp"] = field.value

                        if field.name == "distance":
                            data["distance_m"] = field.value

                        if field.name == "heart_rate":
                            data["heart_rate"] = field.value

                        if field.name == "altitude":
                            data["altitude"] = field.value

                        if field.name == "speed":
                            data["speed_mps"] = field.value

                    records.append(data)

                # ---------- SESSION ----------
                if frame.name == "session":

                    summary = {
                        "file": file,
                        "distance_km": None,
                        "time_min": None,
                        "avg_hr": None,
                        "ascent_m": None,
                        "descent_m": None
                    }

                    for field in frame.fields:

                        if field.name == "total_distance":
                            summary["distance_km"] = field.value / 1000

                        if field.name == "total_elapsed_time":
                            summary["time_min"] = field.value / 60

                        if field.name == "avg_heart_rate":
                            summary["avg_hr"] = field.value

                        if field.name == "total_ascent":
                            summary["ascent_m"] = field.value

                        if field.name == "total_descent":
                            summary["descent_m"] = field.value

                    summaries.append(summary)

    except Exception as e:
        print("Skipping:", file, e)


# ======================
# DATAFRAME
# ======================

df = pd.DataFrame(records)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["pace_min_km"] = (1000 / df["speed_mps"]) / 60

# ======================
# 5 SECOND SMOOTH
# ======================

df10 = df.set_index("timestamp")

df10 = df10.resample("10s").mean(numeric_only=True)

df10 = df10.reset_index()

df10.to_csv("run_10s_data.csv", index=False)

# ======================
# 1 KM SPLITS
# ======================

df["km"] = (df["distance_m"] // 1000).astype(int)

splits = df.groupby(["file", "km"]).agg(
    distance_m=("distance_m", "max"),
    avg_hr=("heart_rate", "mean"),
    avg_speed=("speed_mps", "mean"),
).reset_index()

splits["pace_min_km"] = (1000 / splits["avg_speed"]) / 60

splits.to_csv("run_1km_splits.csv", index=False)

# ======================
# SUMMARY
# ======================

df_summary = pd.DataFrame(summaries)

df_summary.to_csv("run_summary.csv", index=False)

print("Saved:")
print(" run_summary.csv")
print(" run_1km_splits.csv")
print(" run_5s_data.csv")