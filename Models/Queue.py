"""FIFO queue structure used by breadth-first operations and staged inserts."""


class Queue:
    """Simple FIFO queue implementation used for sequential flight inserts."""

    def __init__(self):
        self._data = []  # _data is the list where the elements are stored

    # method that allows adding an element to the queue
    # item: element to add
    def enqueue(self, item):
        self._data.append(item)

    # method that removes the first element of the queue
    # returns: the removed element
    def dequeue(self):
        if self.is_empty():
            raise Exception("The queue is empty")
        return self._data.pop(0)

    # method that checks whether the queue is empty or not
    # returns: a boolean. True if the queue has no elements, False otherwise
    def is_empty(self):
        return len(self._data) == 0

    # method that returns the first element of the queue
    def front(self):
        if self.is_empty():
            raise Exception("The queue is empty")
        return self._data[0]