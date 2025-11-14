import asyncio
from summarizer_service import map_reduce_summarizer

async def main():
    input_file = 'example_input.json'
    print(f"--- Start Summraize: {input_file} ---")
    
    final_summary = await map_reduce_summarizer(input_file)
    
    print("\n==============================================")
    print("           (Final Summary)")
    print("==============================================")
    print(final_summary)
    print("\n--- Success ---")

if __name__ == "__main__":
    asyncio.run(main())