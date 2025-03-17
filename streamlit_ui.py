# -*- coding: utf-8 -*-
import streamlit as st
import ollama
import app
import logging
import jieba_entity_extractor
import jieba_knowledge_retriever

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


with st.sidebar:
    st.title('省立三院ChatMedical医疗大模型')
    st.markdown('---')
    st.markdown('·海量医学知识')
    st.markdown('·大模型本地部署')
    st.markdown('·知识图谱检索增强')
    st.image('images/graphrag.png',caption='医学知识图谱')
    st.markdown('---')
    st.markdown('<div style="text-align: center;">created by 信息科刘文强 2025.03 </div>', unsafe_allow_html=True)

st.title('💬ChatMedical医疗大模型')
st.caption('🚀 一个中文医疗对话系统，基于deepseek和neo4j 开发。')
if "messages" not in st.session_state:
    st.session_state["messages"]=[{"role": "assistant", "content": "你好，我是ChatMedical医疗大模型，你可以问我医疗相关的问题，比如疾病、症状、药品等。"}]
def append_message(role,content):
    st.session_state.messages.append({"role": role, "content": content})
    st.chat_message(role).write(content)

def handle_user_input(user_put):
    if not user_put.strip():
        return "请输入有效问题"

    try:
        entities=app.entity_extractor.extract_entities(user_put)
        logging.info(f"获取的实体信息：{entities}")
        if not isinstance(entities,dict):
            raise ValueError("实体提取结果格式错误")
        disease_name=entities.get("disease",[None])[0] if entities.get("disease") else None
        disease_info = {}

        if disease_name:
            disease_info=app.knowledge_retriever.retrieve_disease_info(disease_name)
            logging.debug(f"疾病详细信息：{disease_info}")
            if not isinstance(disease_info,dict):
                raise ValueError("疾病信息格式错误")
        else:
            logging.debug("未找到疾病名称，疾病信息为空")
        kg_data=app.knowledge_retriever.retrieve_related_info(entities)
        logging.debug(f"关联信息：{kg_data}")
        if not isinstance(kg_data,list):
            raise ValueError("知识信息格式错误")

        final_prompt=app.build_rag_prompt(st.session_state.messages, user_put,kg_data,disease_info)
        logging.debug(f"构建的提示：{final_prompt}")
        response=app.generate_response_with_ollama(final_prompt)
        logging.debug(f"模型响应：{response}")
    except Exception as e:
        logging.error(f"处理用户输入时发生错误: {str(e)}")
        response=f"模型调用失败，请稍后重试"
    return response

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_put:=st.chat_input("请输入您的问题"):
    append_message("user",user_put)

    with st.chat_message("user"):
        st.write(user_put)
        st.write("正在思考...")

    response=handle_user_input(user_put)
    append_message("assistant",response)


st.balloons()


