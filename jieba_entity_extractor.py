# -*- coding: gbk -*-
import jieba
import jieba.posseg as pseg

class EntityExtractor:
    def __init__(self,entity_files):
        '''��ʼ��ʵ���ȡ��'''
        self.entity_files =entity_files
        self.load_entities()

    # def load_entities(self):
    #     self.entities={entity_type:set() for entity_type in self.entity_files}
    #     for entity_type,path in self.entity_files.items():
    #         with open(path,'r') as f:
    #             self.entities[entity_type].update(line.strip() for line in f)
    #         #����Զ�����Ա�ǩ
    #         for word in self.entities[entity_type]:
    #             jieba.add_word(word,tag=f'n_{entity_type}')
    def load_entities(self):
        self.entities = {entity_type: set() for entity_type in self.entity_files}
        for entity_type, paths in self.entity_files.items():
            # ����·���б�
            for path in paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.entities[entity_type].update(line.strip() for line in f)
                except FileNotFoundError:
                    print(f"�ļ� {path} δ�ҵ���")
            # ����Զ�����Ա�ǩ
            for word in self.entities[entity_type]:
                jieba.add_word(word, tag=f'n_{entity_type}')



    def extract_entities(self,text):
        '''
        ���ı�����ȡʵ��
        :param text:
        :return: �ֵ�
        '''
        words=pseg.cut(text)
        tap_mapping={f'n_{k}': k for k in self.entity_files.keys()}
        result={v:[] for v in tap_mapping.values()}
        for word,flag in words:
            if flag in tap_mapping:
                entity_type=tap_mapping[flag]
                result[entity_type].append(word)
        return result
