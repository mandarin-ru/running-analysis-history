import os
import pandas as pd
import fitdecode

WORKOUT_DIR = "workouts"

all_records = []

for file in os.listdir(WORKOUT_DIR):
    if not file.endswith(".fit"):
        continue

    path = os.path.join(WORKOUT_DIR, file)

    print("Reading:", file)

    try:
        with fitdecode.FitReader(path) as fit:

            for frame in fit:

                if frame.frame_type == fitdecode.FIT_FRAME_DATA:

                    row = {
                        "file": file,
                        "message_type": frame.name
                    }

                    # Забираем вообще все поля
                    for field in frame.fields:
                        row[field.name] = field.value

                    all_records.append(row)

    except Exception as e:
        print("Skip file:", file, e)

df = pd.DataFrame(all_records)

df.to_csv("all_workouts_raw.csv", index=False)

print("Saved all_workouts_raw.csv")