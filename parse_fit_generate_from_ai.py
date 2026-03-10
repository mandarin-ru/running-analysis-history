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
                "max_hr": None,
                "avg_speed": None,
                "pace_min_per_km": None
            }

            lap_number = 0

            for frame in fit:

                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue

                # ===== SESSION =====
                if frame.name == "session":

                    distance = frame.get_value("total_distance") or 0
                    duration = frame.get_value("total_timer_time") or 0
                    avg_speed = frame.get_value("avg_speed")

                    session_data["date"] = frame.get_value("start_time")
                    session_data["distance_km"] = distance / 1000
                    session_data["duration_sec"] = duration
                    session_data["avg_hr"] = frame.get_value("avg_heart_rate")
                    session_data["max_hr"] = frame.get_value("max_heart_rate")
                    session_data["avg_speed"] = avg_speed

                    if avg_speed:
                        session_data["pace_min_per_km"] = (1000 / avg_speed) / 60

                # ===== LAP =====
                if frame.name == "lap":

                    lap_number += 1

                    lap_rows.append({
                        "file": file,
                        "lap": lap_number,
                        "distance_m": frame.get_value("total_distance"),
                        "time_sec": frame.get_value("total_timer_time"),
                        "avg_hr": frame.get_value("avg_heart_rate"),
                        "avg_speed": frame.get_value("avg_speed")
                    })

        summary_rows.append(session_data)

    except Exception as e:
        print("Skipping file:", file, e)
        continue


# ===== SAVE =====
pd.DataFrame(summary_rows).to_csv(
    "training_summary.csv",
    index=False
)

pd.DataFrame(lap_rows).to_csv(
    "training_laps.csv",
    index=False
)

print("Export completed")