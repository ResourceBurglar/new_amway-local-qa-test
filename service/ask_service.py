from langchain.document_loaders import DirectoryLoader
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from config.base_config import *
from content.prompt_template_cv import *


def ask(
    ques: str,
    glob: str,
    stuff_prompt_input_variables: list[str] = STUFF_PROMPT_INPUT_VARIABLES,
    stuff_prompt_template: str = STUFF_PROMPT_TEMPLATE,
    refine_prompt_input_variables: list[str] = REFINE_PROMPT_INPUT_VARIABLES,
    refine_input_template: str = REFINE_INPUT_TEMPLATE,
    refine_prompt_quest_variables: list[str] = REFINE_PROMPT_QUEST_VARIABLES,
    refine_quest_template: str = REFINE_QUEST_TEMPLATE,
    chain_type: str = SPLIT_CHUNK_TYPE,
    split_chunk_size: int = SPLIT_CHUNK_SIZE,
    split_chunk_overlap: int = SPLIT_CHUNK_OVERLAP
) -> str:
    loader = DirectoryLoader(path=CONTENT_PATH, glob=str("**/"+glob))
    docs = loader.load()
    print(f"####解析的文档数量有：{len(docs)}")
    print(f"####第一个文档长度有：{len(docs[0].page_content)}")

    split_docs = RecursiveCharacterTextSplitter(
        chunk_size=split_chunk_size,
        chunk_overlap=split_chunk_overlap
    ).split_documents(docs)
    print(f"####Chunk长度策略：", split_chunk_size)
    print(f"####Chunk重叠策略：", split_chunk_overlap)
    print(f"####切割后的文件数量有：{len(split_docs)}")

    if chain_type == 'stuff':
        prompt = PromptTemplate(template=stuff_prompt_template, input_variables=stuff_prompt_input_variables)
        return load_qa_chain(
            llm=OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, max_tokens=1024),
            prompt=prompt,
            chain_type='stuff'
        ).run(input_documents=split_docs, question=ques)
    elif chain_type == 'refine':
        refine_prompt = PromptTemplate(
            input_variables=refine_prompt_input_variables,
            template=refine_input_template,
        )
        question_prompt = PromptTemplate(
            input_variables=refine_prompt_quest_variables,
            template=refine_quest_template,
        )
        return load_qa_chain(
            llm=OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, max_tokens=OPENAI_OUTPUT_TOKEN_LENGTH),
            question_prompt=question_prompt,
            refine_prompt=refine_prompt,
            chain_type='refine',
        ).run(input_documents=split_docs, question=ques)

