import types
from typing import Union
from typing import Optional

class Sorting:
    class Binpacking(object):
        class Bin(object):
            def __init__(self, size: Union[float, int], buffer: Union[float, int] = 0):
                self.items  = []
                self.size   = size
                self.sum    = 0
                self.buffer = buffer
                self.full   = False

            def doesFit(self, size: Union[float, int]) -> bool:
                return (self.sum + size <= self.size + self.buffer and not self.full) or self.size == -1

            def addItem(self, item: object, size: Union[float, int]) -> bool:
                if not self.doesFit(size = size):
                    return False
                self.items.append(item)
                self.sum += (size, 0)[self.size == -1]
                self.full = self.sum >= self.size
                return True

            def __repr__(self) -> str:
                return "Bin Size: {}/{}\n - Items: {}\n".format(self.sum, self.size, self.items)

        def __init__(self, 
                bins: [float], buffers: [float] = [], 
                expand: Union[list, tuple, float, int] = None, expandbuffer: Union[list, tuple, float, int] = None,
                isGreedy: bool = False, doTrash: bool = True):
            Bin                     = Sorting.Binpacking.Bin
            self.buffers            = buffers + [0] * max(0, len(bins) - len(buffers))
            self.bins               = [Bin(size = _bin, buffer = buffer) for _bin, buffer in zip(bins, self.buffers)]
            self.trash              = Bin(-1)
            self.expand             = expand
            self.expandbuffer       = expandbuffer
            if isinstance(expand, (list, tuple)):
                self.expandbuffer   = [0] if expandbuffer is None else list(expandbuffer)
                self.expandbuffer  += self.expandbuffer + [0] * max(0, len(expand) - len(self.expandbuffer))
                self.expand         = [Bin(size = _bin, buffer = buffer) for _bin, buffer in zip(expand, self.expandbuffer)]
            elif not isinstance(self.expand, (float, int)):
                self.expand         = None
                self.expandbuffer   = None
            elif not isinstance(self.expandbuffer, (float, int)):
                self.expandbuffer   = 0
            self.isGreedy           = isGreedy
            self.doTrash            = doTrash

        def _addBin(self, bin: Bin) -> Bin:
            self.bins.append(bin)
            return bin

        def dump(self, item: object, size: Union[float, int]):
            if self.isGreedy:
                self.bins.sort(key = lambda x : x.sum, reverse = False)
            for _bin in self.bins:
                if _bin.addItem(item = item, size = size):
                    return _bin
            if self.expand is not None:
                if isinstance(self.expand, (list, tuple)):
                    for _bin in self.expand:
                        if _bin.addItem(item = item, size = size):
                            return self._addBin(bin = self.expand.pop(self.expand.index(_bin)))
                else:
                    if size - self.expandbuffer <= self.expand:
                        _bin = Sorting.Binpacking.Bin(size = self.expand, buffer = self.expandbuffer)
                        assert _bin.addItem(item = item, size = size)
                        return self._addBin(bin = _bin)
            if self.doTrash:
                assert self.trash.addItem(item = item, size = size)
            return self.trash
        
        def dumps(self, items: [object], sizes: Union[float, int]):
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
        bins            = [11] * 4,
        isGreedy        = True,
        doTrash         = True,
        expand          = 20,
        expandbuffer    = None
    )
    class TestObject(object):
        def __init__(self, size: int):
            self.size = size

        def getSize(self) -> int:
            return self.size

        def __repr__(self) -> str:
            return "TestObject {}".format(self.size)

    bins.fdumps(
        items   = [TestObject(10), TestObject(10), TestObject(11), TestObject(1), TestObject(2), TestObject(7), TestObject(20), TestObject(15), TestObject(4), TestObject(22)],
        func    = TestObject.getSize
    )
    print(bins)


if __name__ == "__main__":
    test()
