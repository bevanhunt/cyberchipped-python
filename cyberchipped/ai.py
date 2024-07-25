from z3 import *
import json
import mimetypes
from datetime import datetime
from typing import AsyncGenerator, Literal, Optional, Dict, Any, Callable
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from openai import OpenAI
import openai
import aiosqlite
from fastapi import UploadFile
from openai import AssistantEventHandler
from openai.types.beta.threads import Text, TextDelta
from typing_extensions import override
import sqlite3
import inspect
from z3 import Bool, Implies, Solver, sat


def adapt_datetime(ts):
    return ts.isoformat()


# Custom converter for datetime
def convert_datetime(ts):
    return datetime.fromisoformat(ts)


# Register the adapter and converter
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)


class EventHandler(AssistantEventHandler):
    def __init__(self, tool_handlers, ai_instance):
        super().__init__()
        self.tool_handlers = tool_handlers
        self.ai_instance = ai_instance
        self.accumulated_value = ""

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        self.ai_instance.accumulated_value += delta.value

    @override
    def on_event(self, event):
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            self.ai_instance.handle_requires_action(event.data, run_id)


class ToolConfig(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class MongoDatabase:
    def __init__(self, db_url: str, db_name: str):
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.threads = self.db["threads"]
        self.messages = self.db["messages"]

    async def save_thread_id(self, user_id: str, thread_id: str):
        await self.threads.insert_one({"thread_id": thread_id, "user_id": user_id})

    async def get_thread_id(self, user_id: str) -> Optional[str]:
        document = await self.threads.find_one({"user_id": user_id})
        return document["thread_id"] if document else None

    async def save_message(self, user_id: str, metadata: Dict[str, Any]):
        metadata["user_id"] = user_id
        await self.messages.insert_one(metadata)

    async def delete_thread_id(self, user_id: str):
        document = await self.threads.find_one({"user_id": user_id})
        thread_id = document["thread_id"]
        openai.beta.threads.delete(thread_id)
        await self.messages.delete_many({"user_id": user_id})
        await self.threads.delete_one({"user_id": user_id})


class SQLiteDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS threads (user_id TEXT, thread_id TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages (user_id TEXT, message TEXT, response TEXT, timestamp TEXT)"
        )
        conn.commit()
        conn.close()

    async def save_thread_id(self, user_id: str, thread_id: str):
        async with aiosqlite.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as db:
            await db.execute(
                "INSERT INTO threads (user_id, thread_id) VALUES (?, ?)",
                (user_id, thread_id),
            )
            await db.commit()

    async def get_thread_id(self, user_id: str) -> Optional[str]:
        async with aiosqlite.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as db:
            async with db.execute(
                "SELECT thread_id FROM threads WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def save_message(self, user_id: str, metadata: Dict[str, Any]):
        async with aiosqlite.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as db:
            await db.execute(
                "INSERT INTO messages (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)",
                (
                    user_id,
                    metadata["message"],
                    metadata["response"],
                    metadata["timestamp"],
                ),
            )
            await db.commit()

    async def delete_thread_id(self, user_id: str):
        async with aiosqlite.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as db:
            async with db.execute(
                "SELECT thread_id FROM threads WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    thread_id = row[0]
                    openai.beta.threads.delete(thread_id)
                    await db.execute(
                        "DELETE FROM messages WHERE user_id = ?", (user_id,)
                    )
                    await db.execute(
                        "DELETE FROM threads WHERE user_id = ?", (user_id,)
                    )
                    await db.commit()


class AI:
    def __init__(self, api_key: str, name: str, instructions: str, database: Any):
        self.client = OpenAI(api_key=api_key)
        self.name = name
        self.instructions = """
            You are an AI assistant that helps users analyze simple logical arguments:

            english_to_logic(argument: str) -> str
            This function analyzes simple logical arguments in English and determines their validity.

            Guidelines for english_to_logic:
            1. The function analyzes simple logical arguments in the form of "If A, then B. A is true. Therefore, B is true."
            2. It uses the Z3 theorem prover to check the validity of the argument.
            3. The function returns a string explaining whether the argument is valid, true, or invalid.

            Example of an english_to_logic input:
            "If it's raining, then the grass is wet. It's raining is true. Therefore, the grass is wet is true."

            Remember:
            - For english_to_logic, provide the entire argument as a single string, following the format: "If A, then B. A is true. Therefore, B is true."
        """ + instructions
        self.model = "gpt-4o-mini"
        self.tools = [{"type": "code_interpreter"}]
        self.tool_handlers = {}
        self.assistant_id = None
        self.database = database
        self.accumulated_value = ""
        self.add_tool(self.english_to_logic)

    async def __aenter__(self):
        assistants = openai.beta.assistants.list()
        for assistant in assistants:
            if assistant.name == self.name:
                openai.beta.assistants.delete(assistant.id)
                break

        self.assistant_id = openai.beta.assistants.create(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools,
            model=self.model,
        ).id
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Perform any cleanup actions here
        pass

    def create_z3_vars(self, statements):
        return {stmt: Bool(stmt) for stmt in statements}

    def add_implications_to_solver(self, solver, implications, vars):
        for antecedents, consequent in implications:
            solver.add(Implies(And(*[vars[ant]
                       for ant in antecedents]), vars[consequent]))

    def add_statements_to_solver(self, solver, statements, vars):
        for statement, value in statements:
            solver.add(vars[statement] == value)

    def parse_argument(self, argument: str):
        prompt = f"""
        Parse the following logical argument into a structured format:

        {argument}

        Return the result as a JSON object with the following structure:
        {{
            "premises": [
                {{
                    "type": "implication",
                    "antecedents": ["A", "B"],
                    "consequent": "C"
                }},
                {{
                    "type": "statement",
                    "statement": "X",
                    "value": true
                }}
            ],
            "conclusion": {{
                "statement": "Y",
                "value": true
            }}
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # or whichever model supports the response_format parameter
            messages=[
                {"role": "system", "content": "You are a logical argument parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        parsed_argument = json.loads(content)
        return parsed_argument

    def create_solver_and_vars(self):
        return Solver(), {}

    def add_premise_to_solver(self, solver, vars, premise):
        if premise['type'] == 'implication':
            antecedents = premise['antecedents']
            consequent = premise['consequent']

            if any('x' in str(ant) or 'y' in str(ant) or 'z' in str(ant) for ant in antecedents + [consequent]):
                # This is a general implication with variables
                x, y, z = Consts('x y z', BoolSort())

                def replace_vars(statement):
                    return str(statement).replace('x', str(x)).replace('y', str(y)).replace('z', str(z))

                ant_vars = [Bool(replace_vars(ant)) for ant in antecedents]
                cons_var = Bool(replace_vars(consequent))

                solver.add(
                    ForAll([x, y, z], Implies(And(*ant_vars), cons_var)))
            else:
                # This is a specific implication
                ant_vars = [self.get_or_create_var(
                    vars, ant) for ant in antecedents]
                cons_var = self.get_or_create_var(vars, consequent)
                solver.add(Implies(And(*ant_vars), cons_var))

        elif premise['type'] == 'statement':
            var = self.get_or_create_var(vars, premise['statement'])
            solver.add(var == premise['value'])

    def check_premise_consistency(self, solver):
        return solver.check() == sat

    def add_transitive_property(self, solver, vars):
        height_vars = {k: v for k, v in vars.items() if "is taller than" in k}
        for var1 in height_vars:
            for var2 in height_vars:
                if var1 != var2:
                    parts1 = var1.split(" is taller than ")
                    parts2 = var2.split(" is taller than ")
                    if len(parts1) == 2 and len(parts2) == 2 and parts1[1] == parts2[0]:
                        var3 = f"{parts1[0]} is taller than {parts2[1]}"
                        if var3 in height_vars:
                            solver.add(
                                Implies(And(vars[var1], vars[var2]), vars[var3]))

    def get_or_create_var(self, vars, statement):
        if statement not in vars:
            vars[statement] = Bool(statement.replace(" ", "_"))
        return vars[statement]

    def check_argument(self, parsed_argument):
        premises = parsed_argument['premises']
        conclusion = parsed_argument['conclusion']

        solver = Solver()
        variables = {}

        # Add premises to the solver
        for premise in premises:
            if premise['type'] == 'implication':
                antecedents = [self.get_variable(
                    variables, ant) for ant in premise['antecedents']]
                consequent = self.get_variable(
                    variables, premise['consequent'])
                solver.add(Implies(And(*antecedents), consequent))
            elif premise['type'] == 'statement':
                var = self.get_variable(variables, premise['statement'])
                solver.add(var if premise['value'] else Not(var))

        # Check if the argument is valid
        conclusion_var = self.get_variable(variables, conclusion['statement'])

        # Check if the negation of the conclusion is unsatisfiable
        solver.push()
        solver.add(Not(conclusion_var)
                   if conclusion['value'] else conclusion_var)
        result = solver.check()
        solver.pop()

        if result == unsat:
            return "valid_and_true"
        elif result == sat:
            return "valid_but_not_always_true"
        else:
            return "invalid_or_inconsistent"

    def get_variable(self, variables, statement):
        if statement not in variables:
            if "and" in statement:
                parts = statement.split(" and ")
                return And(self.get_variable(variables, parts[0]),
                           self.get_variable(variables, parts[1]))
            variables[statement] = Bool(statement.replace(" ", "_"))
        return variables[statement]

    def substitute_variables(self, statement, x, y, z):
        return Bool(statement.replace("x", str(x)).replace("y", str(y)).replace("z", str(z)))

    def get_const(self, name, *args):
        return next(arg for arg in args if str(arg) == name)

    def interpret_result(self, result, conclusion):
        if result == "valid_and_true":
            return f"The argument is valid and true. {conclusion['statement']} is indeed {'true' if conclusion['value'] else 'false'}."
        elif result == "valid_but_not_always_true":
            return f"The argument is valid, but {conclusion['statement']} is not necessarily {'true' if conclusion['value'] else 'false'}."
        elif result == "invalid_or_inconsistent":
            return "The argument is invalid or inconsistent."
        else:
            return result

    def english_to_logic(self, argument: str) -> str:
        try:
            parsed_argument = self.parse_argument(argument)
            result = self.check_argument(parsed_argument)
            return self.interpret_result(result, parsed_argument['conclusion'])
        except Exception as e:
            return f"Error: {str(e)}"

    async def create_thread(self, user_id: str) -> str:
        thread_id = await self.database.get_thread_id(user_id)

        if thread_id is None:
            thread = openai.beta.threads.create()
            thread_id = thread.id
            await self.database.save_thread_id(user_id, thread_id)

        return thread_id

    async def listen(self, audio_file: UploadFile):
        try:
            extension = mimetypes.guess_extension(audio_file.content_type)
            if extension is None:
                raise Exception("Invalid file type")
        except Exception:
            extension = audio_file.filename.split(".")[-1]
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", file=(f"file.{extension}", audio_file.file)
        )
        return transcription.text

    async def text(self, user_id: str, text: str) -> AsyncGenerator[str, None]:
        thread_id = await self.database.get_thread_id(user_id)

        if thread_id is None:
            thread_id = await self.create_thread(user_id)

        self.current_thread_id = thread_id

        # Create a message in the thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=text,
        )

        accumulated_response = []

        class CustomEventHandler(EventHandler):
            def __init__(self, tool_handlers, ai_instance, accumulated_response):
                super().__init__(tool_handlers, ai_instance)
                self.accumulated_response = accumulated_response

            def on_text_delta(self, delta, snapshot):
                self.accumulated_response.append(delta.value)
                self.ai_instance.accumulated_value += delta.value

        event_handler = CustomEventHandler(
            self.tool_handlers, self, accumulated_response)

        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            event_handler=event_handler,
        ) as stream:
            for text in stream.text_deltas:
                yield text
            stream.until_done()

        response_text = "".join(accumulated_response)

        # Save the message to the database
        metadata = {
            "user_id": user_id,
            "message": text,
            "response": response_text,
            "timestamp": datetime.now(),
        }

        await self.database.save_message(user_id, metadata)

    async def conversation(
        self,
        user_id: str,
        audio_file: UploadFile,
        voice: Literal["alloy", "echo", "fable",
                       "onyx", "nova", "shimmer"] = "nova",
        response_format: Literal["mp3", "opus",
                                 "aac", "flac", "wav", "pcm"] = "mp3",
    ):
        thread_id = await self.database.get_thread_id(user_id)

        if thread_id is None:
            thread_id = await self.create_thread(user_id)

        self.current_thread_id = thread_id
        transcript = await self.listen(audio_file)
        event_handler = EventHandler(self.tool_handlers, self)
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=transcript,
        )

        with openai.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()

        response_text = self.accumulated_value

        metadata = {
            "user_id": user_id,
            "message": transcript,
            "response": response_text,
            "timestamp": datetime.now(),
        }

        await self.database.save_message(user_id, metadata)

        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=response_text,
            response_format=response_format,
        )

        return response.response.iter_bytes()

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name in self.tool_handlers:
                handler = self.tool_handlers[tool.function.name]
                inputs = json.loads(tool.function.arguments)
                output = handler(**inputs)
                tool_outputs.append(
                    {"tool_call_id": tool.id, "output": output})

        # Submit all tool_outputs at the same time
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        # Use the submit_tool_outputs_stream helper
        with openai.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(self.tool_handlers, self),
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()

    def add_tool(self, func: Callable):
        sig = inspect.signature(func)
        parameters = {"type": "object", "properties": {}, "required": []}
        for name, param in sig.parameters.items():
            parameters["properties"][name] = {
                "type": "string", "description": "foo"}
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)
        tool_config = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "",
                "parameters": parameters,
            },
        }
        self.tools.append(tool_config)
        self.tool_handlers[func.__name__] = func
        return func


tool = AI.add_tool
