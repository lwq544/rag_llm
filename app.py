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

def build_rag_prompt(messages,user_input,kg_info,disease_info):#3.17���message
    '''
    ���� RAG ��ʾ��
    :param messages: ��ʷ��Ϣ
    :param user_input: �û������ı�
    :param kg_info: ֪ʶͼ������
    :param disease_info: ������ϸ��Ϣ
    :return: ��ʽ�������ʾ��
    '''
    #������ϸ��Ϣ 3.12
    disease_context=f"""
    �������ƣ�{disease_info.get('name','δ֪')}
    ����������{disease_info.get('desc','δ֪')}
    Ԥ����ʩ��{disease_info.get('prevent','δ֪')}
    ���Ʒ�����{disease_info.get('treatment','δ֪')}
    ����{disease_info.get('cause','δ֪')}
    �ò��ʣ�{disease_info.get('get_prob','δ֪')}
    ���Ʒ�ʽ��{disease_info.get('cure_way','δ֪')}
    �����ʣ�{disease_info.get('cure_prob','δ֪')}
    �׸���Ⱥ��{disease_info.get('easy_get','δ֪')}
    �������ڣ�{disease_info.get('cure_lasttime','δ֪')}
   
    """

    context="\n".join(
        set([f"{row['source']}��{row['rel']}��{row['target']}"
         for row in kg_info])
    )

    #3.17�����Ի���ʷ
    convesation_history="\n".join(
        [f"{msg['role']}:{msg['content']}" for msg in messages]
    )

    template="""
    �Ի���ʷ��
    {convesation_history}
    
    ֪ʶ����������
    {disease_context}
    
    ��ع�����Ϣ��
    {context}
    
    ���⣺{question}
    ����רҵ���׶������Ļش�,����ע�ؼ�ҽѧ����
    """
    return template.format( convesation_history=convesation_history, disease_context=disease_context, context=context,question=user_input)

def generate_response_with_ollama(prompt):
    """
    ���� Ollama ����� DeepSeek ģ�����ɻش�
    :param prompt:��������ʾ��
    :return:ģ�����ɵĻش�
    """
    try:
        response=ollama.chat(
            model="deepseek-r1:1.5b",
            messages=[{"role": "user", "content": prompt}],
            options={'temperature': 0.1}
        )
        return response['message']['content']
    except Exception as e:
        return f"ģ�͵���ʧ��1��str(e)"

if __name__=="__main__":
    start_time=time.time()
    messages=[]
    user_input="���տ�����Щ֢״��"
    #��ȡʵ��
    entities=entity_extractor.extract_entities(user_input)
    print("��ȡ��ʵ�壺",entities)

    #����������ϸ��Ϣ
    disease_name=entities.get("disease",[None])[0]
    if disease_name:
        disease_info=knowledge_retriever.retrieve_disease_info(disease_name)
        print("������ϸ��Ϣ��",disease_info)
    else:
        disease_info={}

    #�����ع�����Ϣ
    kg_data=knowledge_retriever.retrieve_related_info(entities)
    print("��ع�����ϵ:",kg_data)

    #������ʾ��
    final_prompt=build_rag_prompt(messages,user_input,kg_data,disease_info)
    print("������ʾ�ʣ�",final_prompt)

    #����ollama���ɻش�
    response=generate_response_with_ollama(final_prompt)
    en_time=time.time()-start_time
    print("���ջش�: ",response)
    print("���ɻش��ʱ��", en_time)

