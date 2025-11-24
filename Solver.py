import random
import heapq

RIGHT = "R"
LEFT = "L"
UP = "U"
DOWN = "D"

class GameBoard:
    RIGHT = "R"
    LEFT = "L"
    UP = "U"
    DOWN = "D"

    def __init__(self):
        is_solvable = False
        while not is_solvable:
            self.nums = []
            for i in range(16):
                while True:
                    j = random.randint(0, 15)
                    if j not in self.nums:
                        self.nums.append(j)
                        break
            self.board = [[self.nums[i + j * 4] for i in range(4)] for j in range(4)]
            is_solvable = self.solvable(self.board)
        self.num_explored = 0
        self.goal = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]]
        self.solution = []
        self.explored = set()

    def solvable(self, state):
        flat = [x for row in state for x in row]

        inv = 0
        for i in range(16):
            for j in range(i + 1, 16):
                if flat[i] != 0 and flat[j] != 0 and flat[i] > flat[j]:
                    inv += 1

        zero_row_from_bottom = 3 - (flat.index(0) // 4)

        return (inv + zero_row_from_bottom) % 2 == 0

    def display_board(self, board=None):
        if board is None:
            for row in self.board:
                print(f"{row}\n")
        else:
            for row in board:
                print(f"{row}\n")

    def to_hashable(self, state):
        return tuple(tuple(row) for row in state)

    def solve(self):
        self.num_explored = 0

        start_state_hashable = self.to_hashable(self.board)
        goal_state_hashable = self.to_hashable(self.goal)

        start = Node(parent=None, action=None, state=start_state_hashable, depth=0)
        frontier = PriorityQueue()
        frontier.add(start, self.manhattan(self.board))

        self.num_explored += 1

        while True:
            if frontier.empty():
                raise Exception("No solution")
            node = frontier.remove()
            # print(f"nodes explored: {self.num_explored}")

            if node.state == goal_state_hashable:
                actions = []
                self.display_board(node.state)
                while node.parent is not None:
                    actions.append(node.action)
                    node = node.parent
                actions.reverse()
                self.solution = actions
                return self.solution

            self.explored.add(node.state)

            current_state_list = [list(row) for row in node.state]

            for action in self.actions(current_state_list):
                _, new_state_list = self.results(action, current_state_list)
                new_state_hashable = self.to_hashable(new_state_list)

                new_depth = node.depth + 1

                if not frontier.contains_state(new_state_hashable) and new_state_hashable not in self.explored:
                    child = Node(state=new_state_hashable, parent=node, action=action, depth=new_depth)
                    g = new_depth
                    h = self.manhattan(new_state_list)
                    f = g + h
                    frontier.add(child, h)
                    self.num_explored += 1

    def find_zero(self, state=None):
        for i in range(4):
            for j in range(4):
                if state is None:
                    if self.board[i][j] == 0:
                        return [i, j]
                else:
                    if state[i][j] == 0:
                        return [i, j]
        return None

    def actions(self, state=None):
        if state is None:
            i, j = self.find_zero()
        else:
            i, j = self.find_zero(state)
        output = []
        if i < 3:
            output.append(UP)
        if i > 0:
            output.append(DOWN)
        if j < 3:
            output.append(LEFT)
        if j > 0:
            output.append(RIGHT)
        return output

    def results(self, action, state):
        output = [row[:] for row in state]
        i, j = self.find_zero(state)
        match action:
            case 'R':
                output[i][j] = output[i][j-1]
                output[i][j-1] = 0
            case 'L':
                output[i][j] = output[i][j+1]
                output[i][j+1] = 0
            case 'D':
                output[i][j] = output[i-1][j]
                output[i-1][j] = 0
            case 'U':
                output[i][j] = output[i+1][j]
                output[i+1][j] = 0
        return action, output


    def manhattan(self, state):
        pass
        dist = 0
        for i in range(4):
            for j in range(4):
                num = state[i][j]
                if num == 0:
                    continue
                solved_x = (num - 1) // 4
                solved_y = (num - 1) % 4
                dist += (abs(solved_x - i) + abs(solved_y - j))
        return dist

class Node:
    def __init__(self, parent, action, state, depth=0):
        self.parent = parent
        self.action = action
        self.state = state
        self.depth = depth

class StackFrontier:
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class PriorityQueue():
    def __init__(self):
        self.heap = []
        self.count = 0

    def add(self, node, priority):
        heapq.heappush(self.heap, (priority, self.count, node.state, node))
        self.count += 1

    def remove(self):
        _, _, _, node = heapq.heappop(self.heap)
        return node

    def empty(self):
        return len(self.heap) == 0

    def contains_state(self, state):
        return any(item_state == state for _, _, item_state,_ in self.heap)



# board = GameBoard()
# board.solve()
# board.display_board()
# print(board.solution)
# print(len(board.solution))
