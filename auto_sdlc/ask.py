from dataclasses import dataclass
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from diskcache import Cache
import platform

cache = Cache('.cache/llm')
if platform.machine() == 'arm64':
    llm = ChatOpenAI()
else:
    llm = Ollama(model="llama-2")


@dataclass
class LLMYesOrNoResponse():
    """LLM Yes or No Response."""
    answer: bool
    full_response: str
    full_question: str

    def __bool__(self) -> bool:
        """Return answer."""
        return self.answer

@cache.memoize()
def get_answer(input: str) -> str:
    """Get answer from LLM."""
    response = llm.invoke(f"Answer the following question: {input}. Answer:")
    return str(response.content)

def yes_or_no(question: str) -> LLMYesOrNoResponse:
    """Get yes or no from LLM."""
    str_answer = get_answer(question)
    if str_answer.lower() in ["y", "yes"]:
        bool_answer = True
    else:
        bool_answer = False
    return LLMYesOrNoResponse(
        answer=bool_answer,
        full_response=str_answer,
        full_question=question,
    )
