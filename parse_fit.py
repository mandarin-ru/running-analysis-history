import os
import pandas as pd
import fitdecode

WORKOUT_DIR = "workouts"

summary_rows = []
lap_rows = []
record_rows = []

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
                "max_speed": None,
                "calories": None
            }

            lap_number = 0

            for frame in fit:

                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue


                if frame.name == "session":

                    session_data["date"] = frame.get_value("start_time")
                    session_data["distance_km"] = (frame.get_value("total_distance") or 0) / 1000
                    session_data["duration_sec"] = frame.get_value("total_timer_time")
                    session_data["avg_hr"] = frame.get_value("avg_heart_rate")
                    session_data["max_hr"] = frame.get_value("max_heart_rate")
                    session_data["avg_speed"] = frame.get_value("avg_speed")
                    session_data["max_speed"] = frame.get_value("max_speed")
                    session_data["calories"] = frame.get_value("total_calories")


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


                if frame.name == "record":

                    record_rows.append({
                        "file": file,
                        "timestamp": frame.get_value("timestamp"),

                        "distance": frame.get_value("distance"),

                        "speed": frame.get_value("speed")
                        if frame.has_field("speed") else None,

                        "heart_rate": frame.get_value("heart_rate")
                        if frame.has_field("heart_rate") else None,

                        "cadence": frame.get_value("cadence")
                        if frame.has_field("cadence") else None,

                        "altitude": frame.get_value("altitude")
                        if frame.has_field("altitude") else None,

                        "step_length": frame.get_value("step_length")
                        if frame.has_field("step_length") else None,

                        "power": frame.get_value("power")
                        if frame.has_field("power") else None,
                    })

        summary_rows.append(session_data)

    except Exception as e:
        print("Skipping file:", file, e)
        continue


# ===== SAVE =====

pd.DataFrame(summary_rows).to_csv("workouts_summary.csv", index=False)
pd.DataFrame(lap_rows).to_csv("workouts_laps.csv", index=False)
pd.DataFrame(record_rows).to_csv("workouts_records.csv", index=False)

print("Saved all CSV files")