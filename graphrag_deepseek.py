from build_medicalgraph import MedicalGraph
import requests
from ollama import Client

# 从知识图谱中检索相关信息
def search_knowledge_graph(handler, question):
    # 这里简单示例，根据疾病名称检索相关症状
    if "症状" in question:
        disease_name = question.split("的")[0]
        query = f"MATCH (d:Disease)-[:has_symptom]->(s:Symptom) WHERE d.name = '{disease_name}' RETURN s.name"
        results = handler.g.run(query).data()
        symptoms = [result['s.name'] for result in results]
        return f"{disease_name}的症状有：{', '.join(symptoms)}"
    return ""

# 调用 Ollama 部署的 DeepSeek 模型
def call_ollama(question, knowledge_info):
    combined_question = f"{question} 知识图谱信息：{knowledge_info}" if knowledge_info else question
    ollama_client=Client(host='http://localhost:11434')
    response=ollama_client.generate(
        model="deepseek-r1:1.5b",
        prompt=combined_question,
        options={'temperature': 0.1}
    )
    return response['response'].strip()


if __name__ == "__main__":
    # 初始化医疗知识图谱
    handler = MedicalGraph()


    # 模拟用户输入问题
    user_question = "百日咳的症状有哪些？"

    # 从知识图谱中检索相关信息
    knowledge_info = search_knowledge_graph(handler, user_question)

    # 调用 Ollama 部署的 DeepSeek 模型
    answer = call_ollama(user_question, knowledge_info)

    print(f"问题: {user_question}")
    print(f"知识图谱信息: {knowledge_info}")
    print(f"大模型回答: {answer}")