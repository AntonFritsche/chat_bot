import pyautogui
import asyncio
import easyocr
import random
import os
import time

from mss import mss
from PIL import Image
from datetime import datetime
from llama_cpp import Llama


class ChatBot:
    def __init__(self, name: str, time: int, model: str, **kwargs):
        super.__init__(**kwargs)
        self.name: str = name
        self.start_time: datetime = datetime.now()
        self.time: int = time
        self.model: str = model
        self.llm = None
        self.session: bool = False

        self.number_messages: int = 0
        self.context_customer: list = []
        self.context_moderator: list = []
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
        pyautogui.moveTo(x=1000, y=1000, duration=1)  # click into the message field
        pyautogui.click()
        pyautogui.typewrite(msg, interval=0.3)
        pyautogui.moveTo(x=1000, y=1000, duration=1)  # click the on the "Send message" button
        pyautogui.click()

        self.number_messages += 1

    def collect_messages(self):
        """collects all messages from the previous chat"""
        pass

    def generate_message(self):
        """generates a message based on the previous messages"""
        system_content = f"""Du bist ein empathischer Begleiter...
        DEIN PROFIL: {self.moderator_data}
        KUNDEN PROFIL: {self.customer_data}
        
        REGELN:
        - Immer individuell formulieren – kein Copy-Paste erlaubt.
        - Groß-/Kleinschreibung und Satzzeichen beachten: ss statt ß schreiben (z. B. Strasse, muessen, Fuss).
        - Immer eine Frage einbauen, um den Chat am Laufen zu halten.
        - Freundlich bleiben, auf Kunden eingehen, Fragen beantworten, Kunden „erziehen“ (sanft lenken).
        - Vom Fake erzählen: peinliche/lustige/erlebnisreiche Stories einbauen → Bindung schaffen, Interesse steigern.
        - Nicht um Bilder betteln
        - Bei „nicht genug Credits“: besonders heiß / animierend / lockend schreiben, damit er auflädt.
        - Bei Reaktivierungen (lange Pause): extra Mühe geben, Fragen stellen, nichts Sinnloses schreiben.
        - Keine festen Treffen vereinbaren: kein Ort, keine Zeit, kein Tag nennen/bestätigen – immer offen/vage lassen („irgendwann mal“, „wäre schön“ etc.).
        - Bei Nummern/Mails: nicht schreiben „ich sehe sie nicht“ – einfach bedanken und vage antworten („hab notiert, melde mich später“).
        """

        full_prompt = f"""<|im_start|>system
        {system_content}<|im_end|>
        <|im_start|>user
        Bisheriger Kontext: {self.context_customer[0]}<|im_end|>
        <|im_start|>assistant
        {self.context_moderator[0]}<|im_end|>
        <|im_start|>user
        {self.context_customer[1]} [[[thinking]]]<|im_end|>
        <|im_start|>assistant
        """

        response = self.llm(
            full_prompt,
            max_tokens=500,
            stop=["<|im_end|>", "user:", "USER:"],
            temperature=0.7
        )

        return response["choices"][0]["text"]

    def collect_customer_data(self):
        """collects the customer's data"""
        with mss() as sct:
            monitor_customer = {"top": 0, "left": 0, "width": 0, "height": 0}
            monitur_customer_custom_data = {"top": 0, "left": 0, "width": 0, "height": 0}

            customer_image = sct.grab(monitor_customer)
            customer_custom_data_image = sct.grab(monitur_customer_custom_data)

            customer_image = Image.frombytes("RGB", customer_image.size, customer_image.bgra, "raw", "BGRX")
            customer_custom_data_image = Image.frombytes("RGB", customer_custom_data_image.size,
                                                         customer_custom_data_image.bgra, "raw", "BGRX")

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
            moderator_custom_data_image = Image.frombytes("RGB", moderator_custom_data_image.size,
                                                          moderator_custom_data_image.bgra, "raw", "BGRX")

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
        self.llm = Llama(
            model_path=self.model,
            n_gpu_layers=-1, # all layers in gpu
            n_ctx=8192, # context size
            n_threads=8, # cpu core for initial load
            verbose=True
        )

    def log_activity(self):
        """logs the activity of the chatbot"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        print(f"Chatbot {self.name} has been active for {uptime} seconds ({uptime / 3600:.2f} hours)")
        print(f"Total number of messages sent: {self.number_messages}")

    def check_prosed_msg(self):
        """checks if a message is being proposed to use"""
        with mss() as sct:
            check_msg_monitor = {"top": 0, "left": 0, "width": 0, "height": 0}
            check_proposed_msg = sct.grab(check_msg_monitor)
            check_proposed_msg = Image.frombytes("RGB", check_proposed_msg.size, check_proposed_msg.bgra, "raw",
                                                  "BGRX")
            check_proposed_msg.save("screenshots/check_proposed_msg.png")

        reader = easyocr.Reader(['de', 'en'], gpu=False)
        proposed_msg = reader.readtext('screenshots/check_proposed_msg.png', detail=0)
        if proposed_msg == "":
            return True
        else:
            return False

    def send_proposed_msg(self):
        """Clicks to the send button for proposed message"""
        pyautogui.moveTo(x=1000, y=1000, duration=1)  # click on the send button
        pyautogui.click()

    async def checks_new_task(self):
        """checks if new tasks are available"""
        while True:
            # task logik
            with mss() as sct:
                waiting_for_session_monitor = {"top": 0, "left": 0, "width": 0, "height": 0}
                waiting_for_session = sct.grab(waiting_for_session_monitor)
                waiting_for_session = Image.frombytes("RGB", waiting_for_session.size, waiting_for_session.bgra, "raw",
                                                      "BGRX")
                waiting_for_session.save("screenshots/waiting_for_session.png")

            reader = easyocr.Reader(['de', 'en'], gpu=False)
            moderator_text = reader.readtext('screenshots/waiting_for_session.png', detail=0)
            if moderator_text == "Please wait for your next session...":
                self.session = True
                return True

            await asyncio.sleep(2)

    async def run(self):
        """runs the chatbot"""
        self.load_llm()
        delta = datetime.now() - self.start_time
        while delta.total_seconds() < self.time:
            if await self.checks_new_task():
                while self.session == True:
                    # random wait time
                    random.seed()
                    random_wait_time = random.random() * 5
                    time.sleep(random_wait_time)

                    # collects data
                    self.collect_messages()
                    self.collect_customer_data()
                    self.collect_moderator_data()

                    # check for pregenerated message
                    if self.check_prosed_msg():
                        self.send_proposed_msg()
                    else:
                        # generate own response
                        answer = self.generate_message()
                        self.write_message(answer)
                        self.log_activity()
                        os.remove("screenshots/customer_data.png")
                        os.remove("screenshots/customer_custom_data.png")
                        os.remove("screenshots/moderator_data.png")
                        os.remove("screenshots/moderator_custom_data.png")
                        os.remove("screenshots/waiting_for_session.png")

            delta = datetime.now() - self.start_time

    async def test(self):
        """runs the chatbot as a test"""
        self.load_llm()
        delta = datetime.now() - self.start_time
        while delta.total_seconds() < self.time:
            if await self.checks_new_task():
                # random wait time
                random.seed()
                random_wait_time = random.random() * 5
                time.sleep(random_wait_time)

                # collects data
                self.collect_messages()
                self.collect_customer_data()
                self.collect_moderator_data()

                # generate a response
                answer = self.generate_message()
                print("\n", answer, "\n")
                self.log_activity()
                os.remove("screenshots/customer_data.png")
                os.remove("screenshots/customer_custom_data.png")
                os.remove("screenshots/moderator_data.png")
                os.remove("screenshots/moderator_custom_data.png")
                os.remove("screenshots/waiting_for_session.png")

            delta = datetime.now() - self.start_time


if __name__ == '__main__':
    # link: https://huggingface.co/mradermacher/Mistral-Nemo-2407-12B-Thinking-Claude-Gemini-GPT5.2-Uncensored-HERETIC-GGUF
    model = "mradermacher/Mistral-Nemo-2407-12B-Thinking-Claude-Gemini-GPT5.2-Uncensored-HERETIC-GGUF"
    # ChatBot("Testbot", 1000, model).run()

