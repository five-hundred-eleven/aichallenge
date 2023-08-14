#!/usr/bin/env python

class Tree:
	def __init__(self, other):
		if not other:
			return Null
		if len(other) == 1:
			self._data = other[0]
			self._prev = Null
			self._next = Null
		else:
			self._data = other[len(other)/2]
			self._prev = Tree(other[len(other)/2:]) 
			self._next = Tree(other[:len(other)/2]) 

