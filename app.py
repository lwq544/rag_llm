# -*- coding: gbk -*-
from jieba_entity_extractor import EntityExtractor
from jieba_knowledge_retriever import knowledgeRetriever
import ollama
import time

ENTITY_FILES={
    "disease":["dict/disease.txt"],
    "symptom":["dict/symptom.txt"],
    "department":["dict/department.txt"],
    "drug":["dict/drug.txt"],
    "food":["dict/food.txt"],
    "producer":["dict/producer.txt"],
    "check":["dict/check.txt"]
}
neo4j_uri="bolt://localhost:7687"
neo4j_user="neo4j"
neo4j_password="Cnmdhg19950523"

entity_extractor=EntityExtractor(ENTITY_FILES)
knowledge_retriever=knowledgeRetriever(neo4j_uri,neo4j_user,neo4j_password)

def build_rag_prompt(messages,user_input,kg_info,disease_info):#3.17添加message
    '''
    构建 RAG 提示词
    :param messages: 历史消息
    :param user_input: 用户输入文本
    :param kg_info: 知识图谱数据
    :param disease_info: 疾病详细信息
    :return: 格式化后的提示词
    '''
    #疾病详细信息 3.12
    disease_context=f"""
    疾病名称：{disease_info.get('name','未知')}
    疾病描述：{disease_info.get('desc','未知')}
    预防措施：{disease_info.get('prevent','未知')}
    治疗方案：{disease_info.get('treatment','未知')}
    病因：{disease_info.get('cause','未知')}
    得病率：{disease_info.get('get_prob','未知')}
    治疗方式：{disease_info.get('cure_way','未知')}
    治愈率：{disease_info.get('cure_prob','未知')}
    易感人群：{disease_info.get('easy_get','未知')}
    治疗周期：{disease_info.get('cure_lasttime','未知')}
   
    """

    context="\n".join(
        set([f"{row['source']}的{row['rel']}是{row['target']}"
         for row in kg_info])
    )

    #3.17构建对话历史
    convesation_history="\n".join(
        [f"{msg['role']}:{msg['content']}" for msg in messages]
    )

    template="""
    对话历史：
    {convesation_history}
    
    知识库检索结果：
    {disease_context}
    
    相关关联信息：
    {context}
    
    问题：{question}
    请用专业且易懂的中文回答,并标注关键医学名词
    """
    return template.format( convesation_history=convesation_history, disease_context=disease_context, context=context,question=user_input)

def generate_response_with_ollama(prompt):
    """
    调用 Ollama 部署的 DeepSeek 模型生成回答
    :param prompt:完整的提示词
    :return:模型生成的回答
    """
    try:
        response=ollama.chat(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": prompt}],
            options={'temperature': 0.1}
        )
        return response['message']['content']
    except Exception as e:
        return f"模型调用失败1：str(e)"

if __name__=="__main__":
    start_time=time.time()
    messages=[]
    user_input="百日咳有哪些症状？"
    #提取实体
    entities=entity_extractor.extract_entities(user_input)
    print("抽取的实体：",entities)

    #检索疾病详细信息
    disease_name=entities.get("disease",[None])[0]
    if disease_name:
        disease_info=knowledge_retriever.retrieve_disease_info(disease_name)
        print("疾病详细信息：",disease_info)
    else:
        disease_info={}

    #检索关关联信息
    kg_data=knowledge_retriever.retrieve_related_info(entities)
    print("相关关联关系:",kg_data)

    #构建提示词
    final_prompt=build_rag_prompt(messages,user_input,kg_data,disease_info)
    print("最终提示词：",final_prompt)

    #调用ollama生成回答
    response=generate_response_with_ollama(final_prompt)
    en_time=time.time()-start_time
    print("最终回答: ",response)
    print("生成回答耗时：", en_time)

