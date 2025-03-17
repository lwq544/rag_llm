# -*- coding: gbk -*-
from neo4j import GraphDatabase
class knowledgeRetriever:
    def __init__(self,uri,user,password):
        self.uri="bolt://localhost:7687"
        self.user="neo4j"
        self.password="Cnmdhg19950523"
        self.driver=GraphDatabase.driver(self.uri,auth=(self.user,self.password))

    #获取疾病属性
    def retrieve_disease_info(self,disease_name):
        """
        检索疾病详细信息
        :param disease_name:疾病名字
        :return: 疾病信息字典
        """
        query=(f"MATCH (d:Disease) where d.name='{disease_name}' "
               f"RETURN "
               f"d.name as name,"
               f"d.desc as desc,"
               f"d.prevent as prevent,"
               f"d.cause as cause,"
               f"d.get_prob as get_prob,"
               f"d.cure_way as cure_way,"
               f"d.cure_prob as cure_prob,"
               f"d.easy_get as easy_get,"
               f"d.cure_lasttime as cure_lasttime"
               )
        with self.driver.session() as session:
            result=session.run(query,disease_name=disease_name)
            return result.single().data()

    #3.12新增
    def retrieve_related_info(self,entities):
        '''
        根据实体检索知识
        :param entities:
        :return:
        '''
        cypher_queries=[]
        if entities.get('disease'):#疾病相关的所有关系都抽出来
            cypher_queries.append(
                f"MATCH (d:Disease)-[r]->(t) where d.name in {entities['disease']}"
                f"RETURN d.name as source,type(r) as rel,t.name as target"
            )
        if entities.get('check'):
            cypher_queries.append(
                f"MATCH (c:Check)<-[r]-(e) where c.name in {entities['check']}"
                f"RETURN e.name as source,type(r) as rel,c.name as target"
            )
        if entities.get('drug'):
            cypher_queries.append(
                f"MATCH (d:Drug)<-[r]-(t) where d.name in {entities['drug']}"
                f"RETURN d.name as source,type(r) as rel,t.name as target"
            )
        if entities.get('symptom'):
            cypher_queries.append(
                f"MATCH (s:Symptom)<-[r]-(d) where s.name in {entities['symptom']}"
                f"RETURN s.name as source,type(r) as rel,d.name as target"
            )
        if entities.get('food'):
            cypher_queries.append(
                f"MATCH (f:Food)<-[r]-(d) where f.name in {entities['food']}"
                f"RETURN f.name as source,type(r) as rel,d.name as target"
            )
        if entities.get('department'):
            cypher_queries.append(
                f"MATCH (d:Department)<-[r]-(t) where d.name in {entities['department']}"
                f"RETURN d.name as source,type(r) as rel,t.name as target"
            )



        combined_results=[]
        with self.driver.session() as session:
            for query in cypher_queries:
                result=session.run(query)
                combined_results.extend([dict(record) for record in result])
        return combined_results