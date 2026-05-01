"""LIFO stack structure used to keep undo history."""


class Stack:
    """Simple LIFO stack implementation used for undo history."""

    def __init__(self):
        self._data = []  # _data is the list where the elements are stored

    # method that allows adding an element to the stack
    # item: element to add
    def push(self, item):
        self._data.append(item)

    # method that removes the top element of the stack
    # returns: the removed element
    def pop(self):
        if self.is_empty():
            raise Exception("The stack is empty")
        return self._data.pop()

    # method that checks whether the stack is empty or not
    # returns: a boolean. True if the stack has no elements, False otherwise
    def is_empty(self):
        return len(self._data) == 0

    # method that returns the element at the top of the stack
    def peek(self):
        if self.is_empty():
            raise Exception("The stack is empty")
        return self._data[-1]