"""FIFO queue structure used by breadth-first operations and staged inserts."""


class Queue:
    """Simple FIFO queue implementation used for sequential flight inserts."""

    def __init__(self):
        self._data = []  # _data is the list where the elements are stored

    def enqueue(self, item):
        """Add an item to the end of the queue."""
        self._data.append(item)

    def dequeue(self):
        """Remove and return the item at the front of the queue."""
        if self.is_empty():
            raise Exception("The queue is empty")
        return self._data.pop(0)

    def is_empty(self):
        """Return True when the queue has no elements."""
        return len(self._data) == 0

    def front(self):
        """Return the item at the front without removing it."""
        if self.is_empty():
            raise Exception("The queue is empty")
        return self._data[0]
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