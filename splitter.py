from graph import Graph, Tree
import re, copy

payments = []
bill = []
payment_methods = {}
payment_graph = Graph()
tolerance = 0

def get_sub_payments(subset_mark):
	global payments
	ones = [x for x, y in enumerate(subset_mark) if y != '0']		
	n = len(ones)
	if n == 1: return

	sub_bill = [bill[i] for i in ones]
        sub_total_tolerance = sum([x[1] for x in sub_bill])
	sub_payments = []

	temp_bill = copy.deepcopy(bill)
	mark = list(subset_mark)
	while True:
		for i in ones:
			temp_mark = copy.deepcopy(mark)
			temp_mark[i] = '0'
			if subgraph(''.join(temp_mark)).is_connected():

				methods = []
				a = temp_bill[i][0]
				temp_sub_bill = [temp_bill[x][0] for x in ones]
				for p in temp_sub_bill:
					if p in payment_graph.node_neighbors[a]:
						b = p
						break
				for j in payment_methods:
					if (a in payment_methods[j]) and (b in payment_methods[j]):
						methods.append(j)
				pay = (a, b, - temp_bill[i][1] + sub_total_tolerance / float(n), methods)
				if pay[2]<0: pay = (pay[1], pay[0], -pay[2], pay[3])
				sub_payments.append(pay)
				for k in range(0, len(temp_bill)):
					if temp_bill[k][0] == b:
						temp_bill[k] = b, temp_bill[k][1] + \
							temp_bill[i][1] - sub_total_tolerance / float(n)

				mark[i] = '0'
				ones.remove(i)
				break
		if len(ones) == 1: break

	payments += sub_payments

def is_zerosum(subset_mark):
	subsum = 0
	ones = [x for x, y in enumerate(subset_mark) if y != '0']		
	n = len(ones)
	for i in ones: subsum += bill[i][1]
	if (abs(round(subsum, 2)) <= tolerance * n): return True
	return False

def subgraph(subset_mark):
	g = copy.deepcopy(payment_graph)
	zeros = [x for x, y in enumerate(subset_mark) if y == '0']
	nodes = [bill[x][0] for x in zeros]		
	g.delete_nodes(nodes)
	return g

def generate_graph():
	global payment_graph

	graph = []
	for i in payment_methods:
		l = payment_methods[i]
		for j in range(0, len(l)-1):	
			for k in range(j+1, len(l)):
				if not (l[j], l[k]) in graph:
					if not (l[k], l[j]) in graph: graph.append((l[j], l[k]))

	payment_graph = Graph()
	payment_graph.add_nodes([x[0] for x in bill])
	for i in graph: payment_graph.add_edge(i)

def subtract(a, b):
	subtraction = [int(list(b)[i])-int(list(a)[i]) for i in range(0, len(bill))]
	return subtraction

def is_subset(a, b):
	subtraction = subtract(a, b)
	if subtraction == map(abs, subtraction):
		return True
	else:
		return False

def get_balances(init_bill):
	num = len(init_bill)
	all_expenses = sum([x[1] for x in init_bill])
	avg_expense = all_expenses / float(num)
	balances = {}
	for i in init_bill:
		balances[i[0]] = (i[1], 0)
	for p in payments:
		balances[p[0]] = (balances[p[0]][0], balances[p[0]][1] + p[2])
		balances[p[1]] = (balances[p[1]][0], balances[p[1]][1] - p[2])
	balances_list = []
	for i in range(0, len(init_bill)):
		name = init_bill[i][0]
		balances_list.append((name, balances[name][0], balances[name][1], \
			balances[name][0] + balances[name][1] - avg_expense))
	return balances_list

def get_payments(init_bill, methods, t):
	global bill, payments, tolerance, payment_methods
	payments = []
	tolerance = t
	payment_methods = methods
	num = len(init_bill)
	all_expenses = sum([x[1] for x in init_bill])
	avg_expense = all_expenses / float(num)
	bill = [(x[0], x[1] - avg_expense) for x in init_bill]
	generate_graph()

	# go through all subsets
	subset_marks = [str(bin(x)[2:].zfill(num)) for x in range(1, 2 ** num)]
	zerosums = [[] for x in range(0, num)] # subsets which have zero sums
	for i in subset_marks:
		complement_set = bin(2 ** num - 1 - int(i, 2))[2:].zfill(num)
		# check the subset sum
		if not is_zerosum(i): continue
		if not is_zerosum(complement_set): continue
		# check the subset connectivity
		if not subgraph(i).is_connected(): continue
		if not subgraph(complement_set).is_connected(): continue

		n = len(re.sub(r'0', r'', i))
		zerosums[n-1].append(i)
	if zerosums[-1] == []: return [None], None
	tree = Tree()
	for i in range(num-1, -1, -1):
		for j in zerosums[i]:
			level = 0
			father = None
			for k in tree.nodes():
				if (is_subset(j, k)) and (tree.level[k] > level):
					complement = ''.join(map(str, subtract(j, k)))
					if is_zerosum(complement) and subgraph(complement).is_connected():
						level = tree.level[k]
						father = k
			tree.add_node(j, father)
	tree.add_node('0'.zfill(num), tree.final_node)
	node = tree.final_node

	#generate payments
	while True:
		if tree.father_node[node] == None: break
		complement_set = ''.join(map(str, [int(list(tree.father_node[node])[i]) \
			- int(list(node)[i]) for i in range(0, num)]))
		if int(complement_set) != 0:
			get_sub_payments(complement_set)
		node = tree.father_node[node]

	balances = get_balances(init_bill)
	balances = [(x[0], round(x[1],2 ), round(x[2], 2), round(x[3], 2)) for x in balances]
	payments = [(x[0], x[1], round(x[2], 2), x[3]) for x in payments]
	return payments, balances

init_bill=[('A',9),('B',12),('C',11),('D',4),('E',6),('F',1),('G',0)]
methods = {
     	'cash': ['A','B','E','F','G'],
 	'check':['B','C','D','E','G']
    }	
t = 1
print get_payments(init_bill, methods, t)
