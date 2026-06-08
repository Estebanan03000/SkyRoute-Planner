"""LIFO stack structure used to keep undo history."""


class Stack:
    """Simple LIFO stack implementation used for undo history."""

    def __init__(self):
        self._data = []  # _data is the list where the elements are stored

    def push(self, item):
        """Push an item onto the stack."""
        self._data.append(item)

    def pop(self):
        """Remove and return the top item from the stack."""
        if self.is_empty():
            raise Exception("The stack is empty")
        return self._data.pop()

    def is_empty(self):
        """Return True when the stack has no elements."""
        return len(self._data) == 0

    def peek(self):
        """Return the top element without removing it."""
        if self.is_empty():
            raise Exception("The stack is empty")
        return self._data[-1]
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