#!/usr/bin/env python3

class HashedDict (dict):

    def __keytransform__(self, key):
        return self.key_table[key]

    def __keytransforminverse__(self, key):
        for k, v in self.key_table.items():
           if v == key:
              return k

    def __init__(self, key_table={}, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        return super(HashedDict,self).__getitem__(self.__keytransform__(key))

    def __str__(self):
        return str( {self.__keytransforminverse__(k): v for k, v in self.items()} )

    def __repr__(self):
        return repr( {self.__keytransforminverse__(k): v for k, v in self.items()} )

    def _get (self, key):
        return super(HashedDict,self).__getitem__(key)
    def _str (self):
        return super(HashedDict,self).__str__()
    def _repr (self):
        return super(HashedDict,self).__repr__()

