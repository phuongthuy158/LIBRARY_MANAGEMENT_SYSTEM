# custom_hash_table.py

class HashTable:
    def __init__(self, size=100): 
        self.size = size
        self.table = [[] for _ in range(self.size)] 

    def _hash_function(self, key):
        h = 8 
        for char_val in str(key).encode('utf-8'):
            h = (h * 31 + char_val) % self.size
        return h 

    def __setitem__(self, key, value):
        hashed_key = self._hash_function(key)
        bucket = self.table[hashed_key]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value) 
                return
        bucket.append((key, value))

    def __getitem__(self, key):
        hashed_key = self._hash_function(key)
        bucket = self.table[hashed_key]

        for k, v in bucket:
            if k == key:
                return v
        raise KeyError(f"Key '{key}' not found in HashTable.")

    def __delitem__(self, key):
        hashed_key = self._hash_function(key)
        bucket = self.table[hashed_key]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return
        raise KeyError(f"Key '{key}' not found in HashTable.")

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __len__(self):
        count = 0
        for bucket in self.table:
            count += len(bucket)
        return count

    def items(self):
        for bucket in self.table:
            for key, value in bucket:
                yield key, value
    
    def values(self):
        for bucket in self.table:
            for _, value in bucket:
                yield value
    
    def keys(self):
        for bucket in self.table:
            for key, _ in bucket:
                yield key

    def clear(self):
        self.table = [[] for _ in range(self.size)]

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
        