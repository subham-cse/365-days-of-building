# Day 178: GIL CPU Contention and Zero-Copy Shared Memory IPC

**Language / Domain**: Python3

**The Core Concept / "Did You Know?"**:
CPython utilizes a **Global Interpreter Lock (GIL)**, a mutual exclusion lock preventing multiple OS threads from executing Python bytecodes simultaneously. While Python threads work well for I/O-bound tasks (network/file operations), multithreading CPU-bound workloads on multi-core processors actually slows execution down due to lock contention overhead!

To achieve true parallelism for CPU-bound tasks, Python developers use `multiprocessing`. However, transferring large data arrays between processes via standard `multiprocessing.Queue` involves expensive pickle serialization. The optimal high-performance path uses **`multiprocessing.shared_memory`** to share zero-copy shared memory blocks across process boundaries.

**The Code Snippet**:

```python
import time
from multiprocessing import Process, shared_memory
import numpy as np

def compute_in_shared_memory(shm_name, shape, dtype):
    # Attach to existing shared memory block created by main process
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    
    # Create NumPy array backed by shared memory block (Zero-Copy)
    arr = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    
    # Perform CPU-intensive computation inline
    arr *= 2
    
    # Close process handle to shared memory
    existing_shm.close()

if __name__ == '__main__':
    # 1. Allocate 100 Million 64-bit floats (~800 MB buffer)
    size = 100_000_000
    shape = (size,)
    dtype = np.float64

    # 2. Create Shared Memory Block
    shm = shared_memory.SharedMemory(create=True, size=size * np.dtype(dtype).itemsize)

    # 3. Create main NumPy array backed by shared memory
    main_arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
    main_arr[:] = 5.0 # Initialize data

    print(f"Initial shared array sample: {main_arr[:5]}")

    # 4. Spawn child process passing only the shared memory string handle
    start_time = time.perf_counter()
    p = Process(target=compute_in_shared_memory, args=(shm.name, shape, dtype))
    p.start()
    p.join()
    duration = time.perf_counter() - start_time

    print(f"Updated shared array sample: {main_arr[:5]}")
    print(f"Process execution completed in: {duration:.4f} seconds (Zero-Copy IPC)")

    # 5. Cleanup
    shm.close()
    shm.unlink() # Deallocate shared memory block
```

**Under the Hood / Why It Happens**:
Under CPython, CPU-bound threads fight for `PyEval_SaveThread()` and `PyEval_RestoreThread()`. The OS kernel repeatedly context-switches threads that cannot acquire the GIL, degrading throughput.

`multiprocessing.shared_memory` bypasses CPython serialization completely by utilizing OS-native shared memory primitives (`mmap` / POSIX `shm_open` on Unix, Named File Mapping objects on Windows).

When a worker process maps `shm.name`, the kernel maps the exact physical memory pages into the worker's virtual address space. Modifications to array elements occur directly in shared RAM without CPU serialization, IPC socket transfers, or GIL contention.

**Key Takeaway / Safe Pattern**:
Use `threading` for I/O-bound tasks. Use `multiprocessing` for CPU-bound tasks. When exchanging large matrices or datasets between processes, use `multiprocessing.shared_memory` combined with `NumPy` buffers to avoid serialization overhead.
