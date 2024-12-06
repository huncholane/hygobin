from pathlib import Path
from typing import Dict
from openai import Client
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import Run
import json

from pydantic import BaseModel, Field


class CodegenResponse(BaseModel):
    file_data: Dict[str, str] = Field(
        ...,
        description="The relative path to put the file and the content of the file.",
    )
    run_script: str = Field(..., description="The script to run the code.")
    production_script: str = Field(
        ..., description="The script to run the code in production."
    )
    test_script: str = Field(..., description="The script to test the code.")


class Codegen:
    assistant_data: Dict[str, Dict[str, str]]
    assistant_id = None
    thread_id = None
    session_name: str
    assistant: Assistant
    thread: Thread

    @property
    def is_new_session_data(self):
        return self.assistant_id is None or self.thread_id is None

    def __init__(
        self,
        datadir="~/.hygobin/datadir",
        model="gpt-4o-mini",
        extensions=[
            "*.py",
            "*.html",
            "*.rs",
            "*.sh",
            "*.ts",
            "*.js",
            "*.jsx",
            "*.tsx",
            "*.json",
        ],
        tools=[{"type": "code_interpreter"}],
        instructions="You are a software developer working on a project.",
    ):
        self.datadir = Path(datadir).expanduser()
        self.assistant_file = self.datadir / "sessions.json"
        self.instructions = instructions
        self.tools = tools
        self.model = model
        self.extensions = extensions
        self.assistant_file.touch(exist_ok=True)
        with open(self.assistant_file, "r") as f:
            self.assistant_data = json.load(f)
        self.client = Client()

    def init_session(self):
        # Create a new assistant
        self.assistant = self.client.beta.assistants.create(
            name=self.session_name,
            model=self.model,
            tools=self.tools,
            instructions=self.instructions,
        )
        self.thread = self.client.beta.threads.create()
        self.assistant_id = self.assistant.id
        self.thread_id = self.thread.id
        run = self.client.beta.threads.create_and_run_poll(
            thread=self.thread,
            assistant_id=self.assistant_id,
            model=self.model,
            response_format=CodegenResponse,
        )

    def get_current_file_data(self):
        file_data = {}
        for file in Path(".").rglob(self.extensions):
            with open(file, "r") as f:
                file_data[file.absolute()] = f.read()
        return file_data

    def handle_run(self, run: Run):
        if run.status == "completed":
            message = self.client.beta.threads.messages.retrieve(message_id=run.id)
            print(message)

    def load_session_data(self, session_name: str):
        self.session_name = session_name
        with open(self.assistant_file, "r") as f:
            self.assistant_data = json.load(f)
        try:
            self.assistant_id = self.assistant_data[self.session_name]["assistant_id"]
            self.thread_id = self.assistant_data[self.session_name]["thread_id"]
        except KeyError:
            self.assistant_data[self.session_name] = {}
            self.assistant_id = None
            self.thread_id = None

    def save_session(self):
        self.assistant_data[self.session_name] = {
            "assistant_id": self.assistant_id,
            "thread_id": self.thread_id,
        }
        with open(self.assistant_file, "w") as f:
            json.dump(self.assistant_data, f)
