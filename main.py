import pyautogui
import torch
import asyncio
import easyocr
import random
import os

from mss import mss
from PIL import Image
from datetime import datetime
from transformers import pipeline


class ChatBot:
    def __init__(self, name: str, time: int, llm: str, **kwargs):
        super.__init__(**kwargs)
        self.name: str = name
        self.start_time: datetime = datetime.now()
        self.time: int = time
        self.llm: str = llm
        self.pipe = None

        self.number_messages: int = 0
        self.context: list = []
        self.customer_data: dict = {
            "Name": "",
            "Age": "",
            "City": "",
            "Job": "",
            "Sex Preferences": "",
            "Booked Holidays": "",
            "Others": "",
            "Custom Data": []
        }
        self.moderator_data: dict = {
            "Name": "",
            "Age": "",
            "City": "",
            "Job": "",
            "Sex Preferences": "",
            "Booked Holidays": "",
            "Others": "",
            "Custom Data": []
        }

    def write_message(self, msg: str):
        """writes a message to the textbox in the chat and sends it"""
        pyautogui.moveTo(x=1000, y=1000, duration=1) # click into the message field
        pyautogui.click()
        pyautogui.typewrite(msg, interval=0.08)
        pyautogui.moveTo(x=1000, y=1000, duration=1)
        pyautogui.click()

        self.number_messages += 1

    def collect_messages(self):
        """collects all messages from the previous chat"""
        pass

    def generate_message(self):
        """generates a message based on the previous messages"""
        formatted_message = [{
            "role": "system",
            "content": f"""Du bist ein empathischer Begleiter. Nutze die folgenden Profile für deine Identität und dein Wissen über den Kunden.
            
            DEIN PROFIL:
            {self.moderator_data}
            
            KUNDEN PROFIL:
            {self.customer_data}
            
            RICHTLINIEN:
            - Antworte authentisch und warm.
            - Nutze die vorletzte Nachricht nur als Kontext für die Stimmung.
            - Antworte DIREKT nur auf die aktuellste Nachricht."""
            },
            {"role": "user", "content": f"Bisheriger Kontext: {self.context[0]}"},
            {"role": "assistant", "content": "Verstanden, ich behalte das im Hinterkopf."},
            {"role": "user", "content": self.context[1]}
        ]

        prompt = self.pipe.tokenizer.apply_chat_template(
            formatted_message,
            tokenize=False,
            add_generation_prompt=True
        )

        output = self.pipe(
            prompt,
            max_new_tokens=500,
            do_sample=True,
            temperature=0.75,
            repetition_penalty=1.1
        )
        return output[0]['generated_text']

    def collect_customer_data(self):
        """collects the customer's data"""
        with mss() as sct:
            monitor_customer = {"top": 0, "left": 0, "width": 0, "height": 0}
            monitur_customer_custom_data = {"top": 0, "left": 0, "width": 0, "height": 0}

            customer_image = sct.grab(monitor_customer)
            customer_custom_data_image = sct.grab(monitur_customer_custom_data)

            customer_image = Image.frombytes("RGB", customer_image.size, customer_image.bgra, "raw", "BGRX")
            customer_custom_data_image = Image.frombytes("RGB", customer_custom_data_image.size, customer_custom_data_image.bgra, "raw", "BGRX")

            customer_image.save("screenshots/customer_data.png")
            customer_custom_data_image.save("screenshots/customer_custom_data.png")

        reader = easyocr.Reader(['de', 'en'], gpu=False)
        customer_text = reader.readtext('screenshots/customer_data.png', detail=0)
        customer_custom_text = reader.readtext('screenshots/costumer_custom_data.png', detail=0)

        self.customer_data["Name"] = customer_text[0].split("Name:")[1]
        self.customer_data["Age"] = customer_text[1].split("Age:")[1]
        self.customer_data["City"] = customer_text[2].split("City:")[1]
        self.customer_data["Job"] = customer_text[3].split("Job:")[1]
        self.customer_data["Sex Preferences"] = customer_text[4].split("Sex Preferences:")[1]
        self.customer_data["Booked Holidays"] = customer_text[5].split("Booked Holidays:")[1]
        self.customer_data["Others"] = customer_text[6].split("Others:")[1]

        self.customer_data["Custom Data"] = " ".join(customer_custom_text)

    def collect_moderator_data(self):
        """collects the moderator's data"""
        with mss() as sct:
            monitor_moderator = {"top": 0, "left": 0, "width": 0, "height": 0}
            monitor_moderator_custom_data = {"top": 0, "left": 0, "width": 0, "height": 0}

            moderator_image = sct.grab(monitor_moderator)
            moderator_custom_data_image = sct.grab(monitor_moderator_custom_data)

            moderator_image = Image.frombytes("RGB", moderator_image.size, moderator_image.bgra, "raw", "BGRX")
            moderator_custom_data_image = Image.frombytes("RGB", moderator_custom_data_image.size, moderator_custom_data_image.bgra, "raw", "BGRX")

            moderator_image.save("screenshots/moderator_data.png")
            moderator_custom_data_image.save("screenshots/moderator_custom_data.png")


        reader = easyocr.Reader(['de', 'en'], gpu=False)
        moderator_text = reader.readtext('screenshots/moderator_data.png', detail=0)
        moderator_custom_text = reader.readtext('screenshots/moderator_custom_data.png', detail=0)

        self.moderator_data["Name"] = moderator_text[0].split("Name:")[1]
        self.moderator_data["Age"] = moderator_text[1].split("Age:")[1]
        self.moderator_data["City"] = moderator_text[2].split("City:")[1]
        self.moderator_data["Job"] = moderator_text[3].split("Job:")[1]
        self.moderator_data["Sex Preferences"] = moderator_text[4].split("Sex Preferences:")[1]
        self.moderator_data["Booked Holidays"] = moderator_text[5].split("Booked Holidays:")[1]
        self.moderator_data["Others"] = moderator_text[6].split("Others:")[1]

        self.moderator_data["Custom Data"] = " ".join(moderator_custom_text)

    def load_llm(self):
        """loads the weights of the llm"""
        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.pipe = pipeline(
            "text-generation",
            model=self.llm,
            model_kwargs={
                "torch_dtype": torch.bfloat16,
                "low_cpu_mem_usage": True
            },
            device=device,
        )

    def log_activity(self):
        """logs the activity of the chatbot"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        print(f"Chatbot {self.name} has been active for {uptime} seconds ({uptime / 3600:.2f} hours)")
        print(f"Total number of messages sent: {self.number_messages}")

    async def checks_new_task(self):
        """checks if new tasks are available"""
        while True:
            # task logik
            if pyautogui.locateOnScreen("screenshots/waiting_for_session.png") is not None:
                return True

            await asyncio.sleep(5)

    async def run(self):
        """runs the chatbot"""
        self.load_llm()
        time = datetime.now()
        delta = time - self.start_time
        while delta.total_seconds() < self.time:
            task = await self.checks_new_task.get()

            if task:
                # collects data
                random.seed()
                random_wait_time = random.random() * 5
                time.sleep(random_wait_time)

                self.collect_messages()
                self.collect_customer_data()
                self.collect_moderator_data()

                # generate a response
                answer = self.generate_message()
                self.write_message(answer)
                self.log_activity()
                os.remove("screenshots/customer_data.png")
                os.remove("screenshots/customer_custom_data.png")
                os.remove("screenshots/moderator_data.png")
                os.remove("screenshots/moderator_custom_data.png")

            delta = datetime.now() - self.start_time



if __name__ == '__main__':
    model = "VibeStudio/Nidum-Llama-3.2-3B-Uncensored"

