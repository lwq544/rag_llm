from build_node_relation import DataToNeo4j
import  pandas as pd

test_data=pd.read_excel('test_data_Demo.xls')

def data_extraction():
    #取甲方名称到list
    node_buy_key=[]
    for i in range(len(test_data)):
        node_buy_key.append(test_data['甲方名称'][i])
    #取乙方名字到list
    node_sell_key=[]
    for i in range(len(test_data)):
        node_sell_key.append(test_data['乙方名称'][i])

    #去重
    node_buy_key=list(set(node_buy_key))
    node_sell_key=list(set(node_sell_key))

    # node_list_value=[]
    # for i in range(len(test_data)):
    #     for n in range(1,len(test_data.columns)):
    #         node_list_value.append(test_data[test_data.columns[n]][i])
    #
    # node_list_value=list(set(node_list_value))
    # node_list_value=[str(i) for i in node_list_value]

    return node_buy_key,node_sell_key#,node_list_value


def relation_extration():
    link_dict={}
    sell_list=[]
    money_list=[]
    buy_list=[]

    for i in range(0,len(test_data)):
        money_list.append(test_data[test_data.columns[2]][i])
        sell_list.append(test_data[test_data.columns[1]][i])
        buy_list.append(test_data[test_data.columns[0]][i])

    sell_list=[str(i) for i in sell_list]
    buy_list=[str(i) for i in buy_list]
    money_list=[str(i) for i in money_list]

    link_dict['buy']=buy_list
    link_dict['money']=money_list
    link_dict['sell']=sell_list
    df_data=pd.DataFrame(link_dict)
    print(df_data)
    return df_data


create_data=DataToNeo4j()
create_data.create_node(data_extraction()[0],data_extraction()[1])
create_data.create_relation(relation_extration())

