import os
import time
from datetime import datetime

import langfun as lf
import pyglove as pg
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from redmail import EmailSender

load_dotenv()


class Config:
    def __init__(self, email_receivers):
        self.EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        self.EMAIL_HOST = "smtp.gmail.com"
        self.EMAIL_PORT = 587
        self.SCREENSHOT_PATH = os.path.join("data", "screenshots")
        self.RECEIVERS = email_receivers

        # Ensure paths exist
        os.makedirs(self.SCREENSHOT_PATH, exist_ok=True)


class Notifier:
    def __init__(self, config: Config):
        self.gmail = EmailSender(
            host=config.EMAIL_HOST,
            port=config.EMAIL_PORT,
            username=config.EMAIL_USERNAME,
            password=config.EMAIL_PASSWORD,
            use_starttls=True,
        )
        self.receivers = config.RECEIVERS

    def send_email(self, subject, body, screenshot_path):
        try:
            with open(screenshot_path, "rb") as f:
                screenshot_content = f.read()

            self.gmail.send(
                subject=subject,
                sender=self.gmail.username,
                receivers=self.receivers,
                text=body,
                attachments={
                    os.path.basename(screenshot_path): screenshot_content
                },
            )
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")


class ScreenshotTaker:
    def __init__(self, config: Config, timeFrom_str, timeTo_str):
        self.screenshot_path_loaded = config.SCREENSHOT_PATH
        self.timeFrom = timeFrom_str
        self.timeTo = timeTo_str

    def capture(self):
        timeFrom = int(
            datetime.strptime(self.timeFrom, "%Y-%m-%d %H:%M:%S").timestamp()
            * 1000
        )
        timeTo = int(
            datetime.strptime(self.timeTo, "%Y-%m-%d %H:%M:%S").timestamp()
            * 1000
        )
        timestamp = datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
        screenshot_filename = f"{timestamp}_element.png"
        screenshot_path = os.path.join(
            self.screenshot_path_loaded, screenshot_filename
        )

        with sync_playwright() as p:
            # browser = p.chromium.launch(channel="msedge", headless=False)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            # Load the Grafana dashboard
            page.goto(
                f"https://grafana.cloud.uiam.sk/d/3VVrrINVz/switchboards-floor-6?orgId=1&from={timeFrom}&to={timeTo}"
            )
            page.wait_for_load_state("load", timeout=10000)

            # Locate he element for screenshot
            page.wait_for_selector(
                'section.panel-container[aria-label="Power SwitchBoard-C panel"]',
                timeout=30000,
            )
            element = page.query_selector(
                'section.panel-container[aria-label="Power SwitchBoard-C panel"]'
            )

            # Take the screenshot if element found
            if element:
                time.sleep(5)
                element.screenshot(path=screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
            else:
                print("Element not found.")

            browser.close()

        return screenshot_path


class Anomaly(pg.Object):
    timestamp: str
    description: str
    classification: str
    severity: str
    cause: str
    action: str


class AnomalyDetectionResult(pg.Object):
    anomalies: list[Anomaly]


class AnomalyDetector:
    def __init__(self, config: Config):
        pass

    def detect(self, imgpath):
        with open(imgpath, "rb") as img_file:
            img_data = lf.Image.from_bytes(img_file.read())

        prompt = """
        You are an AI-based anomaly detector monitoring electricity consumption in
        an office environment through visual analysis.
        Your task:
        1. Analyze the input graph ({{my_image}}) and identify anomalies
        in the consumption patterns.
        2. Provide a detailed description of each anomaly, including potential
        causes for sudden changes in electricity usage.
        3. Report exact timestamps (in the format HH:MM)
        for when each anomaly is detected.
        """

        desc = lf.query(
            prompt,
            AnomalyDetectionResult,
            lm=lf.llms.VertexAIGeminiFlash1_5(),
            my_image=img_data,
        )

        output_content = ""
        if desc.anomalies:
            for anomaly in desc.anomalies:
                output_content += f"Timestamp: {anomaly.timestamp}\n"
                output_content += f"Anomaly detected: {anomaly.description}\n"
                output_content += f"Severity: {anomaly.severity}\n"
                output_content += f"Classification: {anomaly.classification}\n"
                output_content += f"Cause: {anomaly.cause}\n"
                output_content += f"Action: {anomaly.action}\n"
                output_content += "-" * 40 + "\n"
        else:
            output_content = "No anomalies detected.\n"

        return output_content, desc.anomalies


class AnomalyDetectionPipeline:
    def __init__(self, email_receivers, timeFrom_str, timeTo_str):
        config = Config(email_receivers)
        self.screenshot_taker = ScreenshotTaker(
            config, timeFrom_str, timeTo_str
        )
        self.anomaly_detector = AnomalyDetector(config)
        self.email_notifier = Notifier(config)

    def run(self):
        print("Running task")
        screenshot_path = self.screenshot_taker.capture()
        anomaly_results, anomalies = self.anomaly_detector.detect(
            screenshot_path
        )

        if anomalies:
            subject = "Anomaly Detection Report"
            body = (
                "Please find the attached screenshot and the anomaly detection report below:\n\n"
                f"{anomaly_results}"
            )
            self.email_notifier.send_email(subject, body, screenshot_path)

        print("Task completed")
