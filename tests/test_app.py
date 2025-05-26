from utils.memory_manager import MemoryManager


def test_app(mem_mgr: MemoryManager):
    print("=== Memory Manager Test App ===")

    while True:
        print("\nChoose an option:")
        print("1 - Add new memory")
        print("2 - Browse all memories")
        print("3 - Search memories by input")
        print("4 - display")
        print("5 - Exit")

        choice = input("Your choice: ").strip()

        if choice == '1':
            text = input("Enter memory text: ").strip()
            tokens = text.split()  # simple tokenization by splitting spaces
            embedding = mem_mgr.embedder.encode(text)
            mem_mgr.add_new_memory(text, embedding, tokens)
            print("Memory added!")

        elif choice == '2':
            mem_mgr.cursor.execute("SELECT * FROM memories")
            memories = mem_mgr.cursor.fetchall()
            if memories:
                print("\n--- Memories ---")
                for mem in memories:
                    print(f"[{mem}]")
            else:
                print("No memories found.")

        elif choice == '3':
            query = input("Enter search query: ").strip()
            try:
                results = mem_mgr.get_memories(query, limit=5)
                if results:
                    print("\n--- Search Results ---")
                    print(f"Found {len(results)} matching memories:")
                    for mem in results:
                        print(f"[{mem}]")
                else:
                    print("No matching memories found.")
            except Exception as e:
                print("Error during search:", e)

        elif choice == "4":
            mem_mgr.get_all_for_view()

        elif choice == '5':
            print("Exiting...")
            break

        else:
            print("Invalid choice, try again.")