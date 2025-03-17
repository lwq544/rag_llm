from py2neo import Node, Relationship
from py2neo import Graph,Subgraph

# 使用 Bolt 协议
test_graph = Graph("bolt://localhost:7687", auth=("neo4j", "Cnmdhg19950523"))
test_graph.delete_all()

node1 = Node("英雄", name="张无忌")
node2 = Node("英雄", name="杨逍", 武力值='100')
node3 = Node("派别", name="明教")

# 存入数据库
test_graph.create(node1)
test_graph.create(node2)
test_graph.create(node3)

#创建节点关系
node1_to_node2 = Relationship(node1, "教主", node2)
node3_to_node1= Relationship(node1, "统领", node3)
node2_to_node3 = Relationship(node2, "师出", node3)

test_graph.create(node1_to_node2)
test_graph.create(node3_to_node1)
test_graph.create(node2_to_node3)

#建一个路径
from py2neo import Path
node4,node5,node6=Node(name='阿大'),Node(name='阿二'),Node(name='阿三')
path_1=Path(node4,'小弟',node5,Relationship(node6,"小弟",node5),node6)
test_graph.create(path_1)
print(path_1)

#创建子图
node7=Node('英雄',name='张翠山')
node8=Node('英雄',name='殷素素')
node9=Node('英雄',name='狮王')

relationship7=Relationship(node1,'生父',node7)
relationship8=Relationship(node1,'生母',node8)
relationship9=Relationship(node1,'义父',node9)
subgraph1=Subgraph([node7,node8,node9],[relationship7,relationship8,relationship9])
test_graph.create(subgraph1)

#创建事务
transaction1=test_graph.begin()
#创建新node
node10=Node('武当',name='张三丰')
transaction1.create(node10)
#创建两个关系
realationn10=Relationship(node1,'师公',node10)
realationn11=Relationship(node7,'妻子',node8)

transaction1.create(realationn10)
transaction1.create(realationn11)
test_graph.commit(transaction1)

node11=Node('英雄',name='韦一笑')
test_graph.create(node11)
test_graph.run('match(n:英雄{name:\'韦一笑\'})delete n')

#删除一个节点及与之相连的关系
test_graph.run('match(n:英雄{name:\'韦一笑\'})detach delete n')


#查询
from py2neo import NodeMatcher
nodes=NodeMatcher(test_graph)
#单个节点，按照label和name查询
node_single=nodes.match('英雄',name='杨逍').first()
print('单节点查询:\n',node_single)

#按label查询所有节点
node_hero=nodes.match('英雄').all()
print('查询结果的数据类型:',type(node_hero))
#x循环打印
i=0
for node in node_hero:
    print('label查询的第{}个：为{}'.format(i,node))
    i+=1