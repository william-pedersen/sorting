import types
from typing import Union
from typing import Optional
import timeit
import numpy as np

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

            def __eq__(self, _bin) -> bool:
                assert isinstance(_bin, type(self))
                return self.sum / (self.size + self.buffer) == _bin.sum / (_bin.size + _bin.buffer)

            def __lt__(self, _bin) -> bool:
                assert isinstance(_bin, type(self))
                return self.sum / (self.size + self.buffer) < _bin.sum / (_bin.size + _bin.buffer)

            def __le__(self, _bin) -> bool:
                assert isinstance(_bin, type(self))
                return self.sum / (self.size + self.buffer) <= _bin.sum / (_bin.size + _bin.buffer)

            def __repr__(self) -> str:
                return f"Bin Size: {self.sum}/{self.size}\n - Items: {self.items}\n"

        def __init__(self, 
                bins: [float], buffers: [float] = [], 
                expand: Union[list, tuple, float, int] = None, expandbuffer: Union[list, tuple, float, int] = None,
                isGreedy: bool = False, doTrash: bool = True
        ):
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

        def _addBin(self, _bin: Bin) -> Bin:
            self.bins.append(_bin)
            return _bin

        def _draw(self):
            import matplotlib.pyplot as plt
            import numpy as np

            
            fig, ax = plt.subplots()
            for _bin in self.bins:
                x = 0
                y = (_bin.sum / _bin.size) - 1
                scale = len(_bin.items) * 100
                color = ['tab:blue'] 
                ax.scatter(x, y, c=color, s=scale, label=color,
                        alpha=0.6, edgecolors='none')

            
            ax.grid(True)
            plt.show()

        def dump(self, item: object, size: Union[float, int]):
            if self.isGreedy:
                _bin = min(self.bins)
                if _bin.addItem(item = item, size = size):
                    return _bin
            else:
                for _bin in self.bins:
                    if _bin.addItem(item = item, size = size):
                        return _bin
            if self.expand is not None:
                if isinstance(self.expand, (list, tuple)):
                    for _bin in self.expand:
                        if _bin.addItem(item = item, size = size):
                            return self._addBin(_bin = self.expand.pop(self.expand.index(_bin)))
                else:
                    if size - self.expandbuffer <= self.expand:
                        _bin = Sorting.Binpacking.Bin(size = self.expand, buffer = self.expandbuffer)
                        assert _bin.addItem(item = item, size = size)
                        return self._addBin(_bin = _bin)
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
                ("", f"\nTrash:\n {self.trash}")[self.doTrash]

        class Test:
            @staticmethod
            def testObjects(doPrint: bool = True, doDraw: bool = False):
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
                        return f"TestObject {self.size}"

                bins.fdumps(
                    items   = [TestObject(10), TestObject(10), TestObject(11), TestObject(1), TestObject(2), TestObject(7), TestObject(20), TestObject(15), TestObject(4), TestObject(22)],
                    func    = TestObject.getSize
                )
                if doPrint: 
                    print(bins)
                if doDraw:
                    bins._draw()

            @staticmethod
            def speedTestObjects(iterations: int, repetitions: int, doDraw: bool = False):
                test = Sorting.Binpacking.Test.testObjects
                test(doPrint = True, doDraw = False)
                timer = timeit.Timer(lambda: test(doPrint = False, doDraw = False))
                #time = timer.timeit(iterations)
                times = timer.repeat(repeat = repetitions, number = iterations)
                time = min(times)
                print(
                    f"Time                           : {time:.2f}s",
                    f" - Iterations                  : {iterations:,}",
                    f" - Repetitions                 : {repetitions:,}",
                    f" - Objects Sorted              : {iterations*10:,}",
                    f" - Time Per Iteration          : {time/iterations*1000:.2f}ms",
                    sep='\n')


                if doDraw:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    from scipy.interpolate import make_interp_spline, BSpline

                            
                    fig, ax = plt.subplots()
                    x   = np.linspace(1, len(times), 200)
                    _y  = make_interp_spline(range(1, len(times) + 1), times)
                    m   = sum(times) / len(times)
                    y   = [y - m for y in _y(x)]
                    ax.set_facecolor('#23272A')
                    fig.patch.set_facecolor('#2C2F33')
                    ax.grid(color = '#2C2F33')
                    ax.spines['bottom'].set_color('#2C2F33')
                    ax.spines['left'].set_color('#2C2F33')
                    ax.spines['top'].set_color('#2C2F33')
                    ax.spines['right'].set_color('#2C2F33')
                    ax.tick_params(axis='x', colors='#FFFFFF')
                    ax.tick_params(axis='y', colors='#FFFFFF')
                    ax.axline((0, 0), (len(times), 0), c = '#7289DA')
                    ax.plot(x, y, c='#FFFFFF')

                            
                    ax.grid(True)
                    plt.show()




def test():
    #test = Sorting.Binpacking.Test.testObjects
    #test(doPrint = True, doDraw = False)
    test = Sorting.Binpacking.Test.speedTestObjects
    test(iterations = 10000, repetitions = 10, doDraw = False)


if __name__ == "__main__":
    test()
