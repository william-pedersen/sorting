import types

class Sorting:
    class Binpacking(object):
        class Bin(object):
            def __init__(self, size: float, buffer: float = 0):
                self.items  = []
                self.size   = size
                self.sum    = 0
                self.buffer = buffer
                self.full   = False

            def doesFit(self, size: float) -> bool:
                return (self.sum + size <= self.size + self.buffer and not self.full) or self.size == -1

            def addItem(self, item: object, size: float) -> bool:
                if not self.doesFit(size = size):
                    return False
                self.items.append(item)
                self.sum += (size, 0)[self.size == -1]
                self.full = self.sum >= self.size
                return True

            def __repr__(self) -> str:
                return "Bin Size: {}/{}\n - Items: {}\n".format(self.sum, self.size, self.items)

        def __init__(self, bins: [float], buffers: [float] = [], 
                isGreedy: bool = False, doTrash: bool = True):
            Bin             = Sorting.Binpacking.Bin
            self.buffers    = buffers + [0] * max(0, len(bins) - len(buffers))
            self.bins       = [Bin(size = _bin, buffer = buffer) for _bin, buffer in zip(bins, self.buffers)]
            self.trash      = Bin(-1)
            self.isGreedy   = isGreedy
            self.doTrash    = doTrash

        def dump(self, item: object, size: float):
            if self.isGreedy:
                self.bins.sort(key = lambda x : x.sum, reverse = False)
            for _bin in self.bins:
                if _bin.addItem(item = item, size = size):
                    return _bin
            if self.doTrash:
                assert self.trash.addItem(item = item, size = size)
            return self.trash
        
        def dumps(self, items: [object], sizes: [float]):
            sizes += [(0, sizes[0])[len(sizes) == 1]] * max(0, len(items) - len(sizes))
            [self.dump(item = item, size = size) for item, size in zip(items, sizes)]

        def fdumps(self, items: [object], func: types.FunctionType):
            sizes = [getattr(item, func.__name__)() for item in items]
            [self.dump(item = item, size = size) for item, size in zip(items, sizes)]

        def adumps(self, items: [object], attr: str):
            sizes = [getattr(item, attr) for item in items]
            [self.dump(item = item, size = size) for item, size in zip(items, sizes)]

        def __repr__(self) -> str:
            return "Bins: \n" + \
                (" {}\n"*len(self.bins)).format(*self.bins) + \
                ("" ,"\nTrash:\n {}".format(self.trash))[self.doTrash]



def test():
    bins = Sorting.Binpacking(
        bins = [11] * 4,
        isGreedy = True,
        doTrash = True
    )
    class TestObject(object):
        def __init__(self, size: int):
            self.size = size

        def getSize(self) -> int:
            return self.size

        def __repr__(self) -> str:
            return "TestObject {}".format(self.size)

    bins.fdumps(
        items = [TestObject(10), TestObject(10), TestObject(11), TestObject(1), TestObject(2), TestObject(7)],
        func = TestObject.getSize
    )
    print(bins)


if __name__ == "__main__":
    test()
