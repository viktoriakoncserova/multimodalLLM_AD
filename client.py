from main import AnomalyDetectionPipeline
import os

if __name__ == "__main__":
    email_receivers = [os.getenv("RECEIVER")]
    timeFrom_str = "2025-04-15 14:00:00"
    timeTo_str = "2025-04-15 14:30:00"

    pipeline = AnomalyDetectionPipeline(
        email_receivers, timeFrom_str, timeTo_str
    )
    pipeline.run()
