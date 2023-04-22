

# cli_components/main.py - Demonstrates the use of the input_processing module in a main application.cli_components/main.py - Demonstrates the use of the input_processing module in a main application.

from input_processing import process_input

def main():
    user_input = input("Enter some text: ")
    processed_input = process_input(user_input)
    print(f"Processed input: {processed_input}")

# if __name__ == '__main__':
#     main()