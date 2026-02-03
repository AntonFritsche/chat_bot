import pyautogui
import torch
import asyncio

from datetime import datetime
from transformers import pipeline


class ChatBot:
    def __init__(self, name: str ,time: int, llm: str, **kwargs):
        super.__init__(**kwargs)
        self.name = name
        self.start_time = datetime.now()
        self.time = time
        self.llm = llm
        self.pipe = None

        self.number_messages = 0
        self.context = []
        self.customer_data = {
            "Name": "",
            "Age": "",
            "City": "",
            "Job": "",
            "Sex Preferences": "",
            "Booked Holidays": "",
            "Others": ""
        }
        self.moderator_data = {
            "Name": "",
            "Age": "",
            "City": "",
            "Job": "",
            "Sex Preferences": "",
            "Booked Holidays": "",
            "Others": ""
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
        pass

    def collect_moderator_data(self):
        """collects the moderator's data"""
        pass

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
            has_task = False
            if has_task:
                return True
            await asyncio.sleep(5)

    async def run(self):
        """runs the chatbot"""
        self.load_llm()
        time = datetime.now()
        delta = time - self.start_time
        while delta.total_seconds() < self.time:
            task = await self.task_queue.get()

            if task:
                # collects data
                self.collect_messages()
                self.collect_customer_data()
                self.collect_moderator_data()

                # generate a response
                answer = self.generate_message()
                self.write_message(answer)
                self.log_activity()

            delta = datetime.now() - self.start_time



if __name__ == '__main__':
    model = "VibeStudio/Nidum-Llama-3.2-3B-Uncensored"

