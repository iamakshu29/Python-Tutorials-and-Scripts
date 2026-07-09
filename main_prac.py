class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

node4 = ListNode(5)
node3 = ListNode(4,node4)
node2 = ListNode(3,node3)
node1 = ListNode(2,node2)

node9 = ListNode(10)
node8 = ListNode(9,node9)
node7 = ListNode(8,node8)
node6 = ListNode(7,node7)
node5 = ListNode(6,node6)


def printNode(head: ListNode):
    while head:
        print(head.val, end="")
        if head.next:
            print(" -> ", end="")
        head = head.next
    print()

printNode(node1)


def reverseNode(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev

head = reverseNode(node1)
printNode(head)