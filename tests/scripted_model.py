"""The only test double for the agents: a scripted agents.Model that stands in for the LLM."""
import json

from agents import Model, ModelResponse, Usage
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText


class ScriptedModel(Model):
    """Plays a fixed list of turns per question: tool calls first, then a final message.

    Records the tools it was offered as the model sees them: name, description and argument schema.
    """

    def __init__(self, script: dict[str, list[list[tuple[str, dict]] | str]]):
        self.script = script
        self.turns: dict[str, int] = {}
        self.tools_seen: list[str] = []
        self.tool_specs: dict[str, tuple[str, dict]] = {}

    async def get_response(self, system_instructions, input, model_settings, tools, *args, **kwargs):
        question = input if isinstance(input, str) else input[0]["content"]
        self.tools_seen = [tool.name for tool in tools]
        self.tool_specs = {tool.name: (tool.description, tool.params_json_schema) for tool in tools}
        turn = self.turns.get(question, 0)
        self.turns[question] = turn + 1
        step = self.script[question][turn]
        if isinstance(step, str):
            output = [ResponseOutputMessage(id="msg", type="message", role="assistant", status="completed",
                                            content=[ResponseOutputText(type="output_text", text=step, annotations=[])])]
        else:
            output = [ResponseFunctionToolCall(type="function_call", id=f"fc{i}", call_id=f"{question[:8]}-{turn}-{i}",
                                               name=name, arguments=json.dumps(arguments, ensure_ascii=False))
                      for i, (name, arguments) in enumerate(step)]
        return ModelResponse(output=output, usage=Usage(requests=1, input_tokens=100, output_tokens=10, total_tokens=110),
                             response_id=None)

    def stream_response(self, *args, **kwargs):
        raise NotImplementedError
