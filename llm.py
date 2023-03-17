from langchain import PromptTemplate
from langchain import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


def format_call(text, fmt:str, llm):
    """
    Create a meeting summary document
    """
    text_splitter = RecursiveCharacterTextSplitter()
    texts = text_splitter.split_text(text)
    return ''.join([llm(PromptTemplate(input_variables=["transcript"], template=fmt).format(transcript=t)) for t in texts])

class LLMFormatter:
    """Takes a transcript and formats it using a prompt template."""
    def __init__(self, oa_key=None, workflow=None) -> None:
        self.workflow = workflow
        self.temp = 0.0
        self.openai_key = oa_key
    
    def format(self, transcript):
        if self.openai_key is None:
            raise Exception("OpenAI Key not set")
        if self.workflow is None:
            raise Exception("Prompt not set")
        try:
            llm = OpenAI(temperature=self.temp)
            result = format_call(transcript, self.workflow, llm)
            return result
        except Exception as e:
            print(e)
            return ''

if __name__ == "__main__":
    lf = LLMFormatter()
    lf.format("This is a test. This is only a test.")