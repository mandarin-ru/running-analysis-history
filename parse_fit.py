import os
import pandas as pd
import fitdecode

WORKOUT_DIR = "workouts"

summary_rows = []
lap_rows = []

for file in os.listdir(WORKOUT_DIR):
    if not file.endswith(".fit"):
        continue

    path = os.path.join(WORKOUT_DIR, file)

    try:
        print("Reading:", file)

        with fitdecode.FitReader(path) as fit:

            session_data = {
                "file": file,
                "date": None,
                "distance_km": None,
                "duration_sec": None,
                "avg_hr": None,
                "max_hr": None
            }

            lap_number = 0

            for frame in fit:

                if frame.frame_type == fitdecode.FIT_FRAME_DATA:

                    if frame.name == "session":

                        session_data["date"] = frame.get_value("start_time")
                        session_data["distance_km"] = (
                            frame.get_value("total_distance") or 0
                        ) / 1000

                        session_data["duration_sec"] = frame.get_value("total_timer_time")
                        session_data["avg_hr"] = frame.get_value("avg_heart_rate")
                        session_data["max_hr"] = frame.get_value("max_heart_rate")

                    if frame.name == "lap":

                        lap_number += 1

                        lap_rows.append({
                            "file": file,
                            "lap": lap_number,
                            "distance_m": frame.get_value("total_distance"),
                            "time_sec": frame.get_value("total_timer_time"),
                            "avg_hr": frame.get_value("avg_heart_rate")
                        })

        summary_rows.append(session_data)

    except Exception as e:
        print("Skipping file:", file, e)
        continue

summary_df = pd.DataFrame(summary_rows)
laps_df = pd.DataFrame(lap_rows)

summary_df.to_csv("workouts_summary.csv", index=False)
laps_df.to_csv("workouts_laps.csv", index=False)

print("Saved CSV files")