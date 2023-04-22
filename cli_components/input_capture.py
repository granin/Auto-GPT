# cli_components/input_capture.py - Demonstrates the use of the input_processing module for capturing user input.cli_components/input_capture.py - Demonstrates the use of the input_processing module for capturing user input.

from input_processing import process_input

def main():
    user_input = input("Please enter some text: ")
    processed_input = process_input(user_input)
    print(f"Processed input: {processed_input}")

if __name__ == "__main__":
    main()