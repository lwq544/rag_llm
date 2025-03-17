import os
import json
from py2neo import Graph, Node

class MedicalGraph:
    def __init__(self):
        cur_dir='/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path=os.path.join(cur_dir,'data/medical2.json')
        self.g=Graph("bolt://localhost:7687", auth=("neo4j", "Cnmdhg19950523"))

    ##读取文件 7类节点 11类关系
    def read_nodes(self):
        checks=[] #检查项目
        departments=[]#科室
        diseases=[]#疾病
        drugs=[]#药品
        foods=[]#食品 分为三类：忌吃、可吃、推荐吃
        producers=[] #药品生产厂商
        symptoms=[] #症状

        disease_infos=[] #疾病信息表,存储疾病相关描述

        #节点关系
        rels_check=[] #疾病-检查
        rels_department=[]#大科室-小科室
        rels_category=[]#疾病-科室
        rels_symptom=[]#疾病-症状
        rels_acompany=[]#疾病-并发症
        rels_noteat=[]#疾病-忌吃食物
        rels_recommandeat=[]#疾病-推荐吃食物
        rels_doeat=[]#疾病-可吃食物
        rels_commonddrug=[]#疾病-通用药品
        rels_recommanddrug=[]#疾病-热门药品
        rels_drug_producer=[]#药品-生产厂商

        count=0
        for data in open(self.data_path):
            disease_dict={}
            count+=1
            print(count)
            data_json=json.loads(data)
            disease=data_json['name']
            disease_dict['name']=disease
            diseases.append(disease)
            disease_dict['desc']=''
            disease_dict['prevent']=''
            disease_dict['cause']=''
            disease_dict['easy_get']=''
            disease_dict['cure_department']=''
            disease_dict['cure_way']=''
            disease_dict['cure_lasttime']=''
            disease_dict['cured_prob']=''

            if 'symptom' in data_json:#症状加入症状实体，同时建立关系
                symptoms+=data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease,symptom])

            if 'acompany' in data_json:#并发加入关系
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease,acompany])

            if 'desc' in data_json:#描述加入属性
                disease_dict['desc']=data_json['desc']

            if 'prevent' in data_json:#预防，加入属性
                disease_dict['prevent']=data_json['prevent']

            if 'cause' in data_json:#病因，加入属性
                disease_dict['cause']=data_json['cause']

            if 'get_prob' in data_json:#发病率，加入属性
                disease_dict['get_prob']=data_json['get_prob']

            if 'easy_get' in data_json:#易感人群
                disease_dict['easy_get']=data_json['easy_get']

            if 'cure_department' in data_json:#治疗科室，分单一科室、双科室情况
                cure_department=data_json['cure_department']
                if len(cure_department)==1:
                    rels_category.append([disease,cure_department[0]])
                if len(cure_department)==2:
                    big=cure_department[0]
                    small=cure_department[1]
                    rels_department.append([small,big])
                    rels_category.append([disease,small])

                disease_dict['cure_department']=cure_department
                departments+=cure_department

            if 'cure_way' in data_json:#治疗途径
                disease_dict['cure_way']=data_json['cure_way']

            if 'cure_lasttime' in data_json:#治疗时长
                disease_dict['cure_lasttime']=data_json['cure_lasttime']

            if 'cured_prob' in data_json:#治疗概率
                disease_dict['cured_prob']=data_json['cured_prob']

            if 'common_drug' in data_json:
                common_drug=data_json['common_drug']
                for drug in common_drug:
                    rels_commonddrug.append([disease,drug])
                drugs+=common_drug

            if 'recommand_drug' in data_json:
                recommand_drug=data_json['recommand_drug']
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease,drug])
                drugs+=recommand_drug

            if 'not_eat' in data_json:
                not_eat=data_json['not_eat']
                for _not in not_eat:
                    rels_noteat.append([disease,_not])

                foods+=not_eat

            if 'do_eat' in data_json:
                do_eat=data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease,_do])

                foods+=do_eat

            if 'recommand_eat'in data_json:
                recommand_eat=data_json['recommand_eat']
                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease,_recommand])

                foods+=recommand_eat

            if 'check' in data_json:
                check=data_json['check']
                for _check in check:
                    rels_check.append([disease,_check])
                checks+=check

            if 'drug_detail' in data_json:
                drug_detail=data_json['drug_detail']
                producer=[i.split('(')[0] for i in drug_detail]
                rels_drug_producer+=[[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers+=producer

            disease_infos.append(disease_dict)

        return set(drugs),set(foods),set(checks),set(departments),set(producers),set(symptoms),set(diseases),disease_infos,\
               rels_check,rels_recommandeat,rels_noteat,rels_doeat,rels_department,rels_commonddrug,rels_drug_producer,\
               rels_recommanddrug,rels_symptom,rels_acompany,rels_category

    '''建立节点'''
    '''普通节点'''
    def create_node(self,label,nodes):
        count=0
        for node_name in nodes:
            node=Node(label,name=node_name)
            self.g.create(node)
            count+=1
            print(count,len(nodes))
        return
    '''创建疾病节点'''
    def create_diseases_nodes(self,disease_info):
        count=0
        for disease_dict in disease_info:
            node=Node("Disease",name=disease_dict['name'],desc=disease_dict['desc'],
                      prevent=disease_dict['prevent'],cause=disease_dict['cause'],
                      easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                      cure_department=disease_dict['cure_department'],
                      cure_way=disease_dict['cure_way'],cured_prob=disease_dict['cured_prob'] )
            self.g.create(node)
            count+=1
            print(count)
        return

    '''创建节点类型模式'''
    def create_graphnodes(self):
        Drugs,Foods,Checks,Departments,Producers,Symptoms,Diseases,disease_infos,\
        rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, \
        rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, \
        rels_acompany, rels_category=self.read_nodes()
        self.create_diseases_nodes(disease_infos)
        self.create_node('Drug',Drugs)
        print(len(Drugs))
        self.create_node('Food',Foods)
        print(len(Foods))
        self.create_node('Check',Checks)
        print(len(Checks))
        self.create_node('Department',Departments)
        print(len(Departments))
        self.create_node('Producer',Producers)
        print(len(Producers))
        self.create_node('Symptom',Symptoms)
        return

    '''创建11种实体关系'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, \
        rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, \
        rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, \
        rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease','Food',rels_recommandeat,'recommand_eat','推荐食谱')
        self.create_relationship('Disease','Food',rels_noteat,'no_eat','忌吃')
        self.create_relationship('Disease','Food',rels_doeat,'do_eat','宜吃')
        self.create_relationship('Department','Department',rels_department,'belongs_to','属于')
        self.create_relationship('Disease','drug',rels_acompany,'common_drug','常用药品')
        self.create_relationship('Producer','Drug',rels_drug_producer,'drug_of','生产药品')
        self.create_relationship('Disease','Drug',rels_recommanddrug,'recommand_drug','好评药品')
        self.create_relationship('Disease','Check',rels_check,'need_check','诊断检查')
        self.create_relationship('Disease','Symptom',rels_symptom,'has_symptom','症状')
        self.create_relationship('Disease','Disease',rels_acompany,'accompany_with','并发症')
        self.create_relationship('Diaease','Department',rels_category,'belongs_to','所属科室')


    '''创建实体关联边'''
    def create_relationship(self,start_node,end_node,edges,rel_type,rel_name):
        count=0
        #去重
        set_edges=[]
        for edge in edges:
            set_edges.append('###'.join(edge))
        all=len(set(set_edges))
        for edge in set(set_edges):
            edge=edge.split('###')
            p=edge[0]
            q=edge[1]
            query_check="match (p:%s)-[rel:%s]->(q:%s) where p.name='%s' and q.name='%s' return rel"%(
                start_node,rel_type,end_node,p,q
            )
            result=self.g.run(query_check)
            if not result.data():
                query="match(p:%s),(q:%s) where p.name='%s' and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q) "%(
                    start_node,end_node,p,q,rel_type,rel_name )
                try:
                    self.g.run(query)
                    count+=1
                    print(rel_type,count,all)
                except Exception as e:
                    print(e)
        return

    '''导出数据'''


if __name__=='__main__':
    handler=MedicalGraph()
    handler.create_graphnodes()
    handler.create_graphrels()









