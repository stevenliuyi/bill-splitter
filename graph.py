class Tree(object):
	def __init__(self):
		self.father_node = {}
		self.level = {}

		self.level[None] = 0
		self.height = 0
		self.final_node = None

	def add_node(self, node, father = None):
		self.father_node[node] = father
		self.level[node] = self.level[father] + 1
		if self.level[node] > self.height:
			self.height = self.level[node]
			self.final_node = node

	def nodes(self):
		return self.father_node.keys()

class Graph(object):
	def __init__(self,*args,**kwargs):
		self.node_neighbors = {}
		self.visited = {}

	def add_nodes(self,nodelist):
		for node in nodelist:
			self.add_node(node)

	def add_node(self,node):
		if not node in self.nodes():
			self.node_neighbors[node] = []

	def add_edge(self,edge):
		u,v = edge
		if(v not in self.node_neighbors[u]) and ( u not in self.node_neighbors[v]):
			self.node_neighbors[u].append(v)
			if(u!=v): self.node_neighbors[v].append(u)

	def delete_node(self,node):
		del self.node_neighbors[node]
		for i in self.node_neighbors:
			if node in self.node_neighbors[i]: self.node_neighbors[i].remove(node)

	def delete_nodes(self,nodelist):
		for node in nodelist:
			self.delete_node(node)

	def nodes(self):
		return self.node_neighbors.keys()

	def depth_first_search(self,root=None):
		order = []
		def dfs(node):
			self.visited[node] = True
			order.append(node)
			for n in self.node_neighbors[node]:
				if not n in self.visited:
					dfs(n)

		if root:
			dfs(root)

		for node in self.nodes():
			if not node in self.visited:
				dfs(node)

		return order

	def is_connected(self):
		order = []
		if len(self.nodes()) == 0: return True
		def dfs(node):
			self.visited[node] = True
			order.append(node)
			for n in self.node_neighbors[node]:
				if not n in self.visited:
					dfs(n)

		dfs(self.nodes()[0])

		for node in self.nodes():
			if not node in self.visited:
				self.visited = {}
				return False
		self.visited = {}
		return True

	def breadth_first_search(self,root=None):
		queue = []
		order = []
		def bfs():
			while len(queue)> 0:
				node  = queue.pop(0)

				self.visited[node] = True
				for n in self.node_neighbors[node]:
					if (not n in self.visited) and (not n in queue):
						queue.append(n)
						order.append(n)

		if root:
			queue.append(root)
			order.append(root)
			bfs()

		for node in self.nodes():
			if not node in self.visited:
				queue.append(node)
				order.append(node)
				bfs()
		return order
