from tests.test_app import test_app
from utils.memory_manager import MemoryManager

def main():
    mem_mgr = MemoryManager()
    test_app(mem_mgr)
    

if __name__ == "__main__":
    main()