import os
import time

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def main():
    filename = "Assistant_Reply.txt"
    last_mtime = None
    last_content = None

    while True:
        try:
            if os.path.exists(filename):
                current_mtime = get_file_mtime(filename)

                if last_mtime is None or current_mtime != last_mtime:
                    with open(filename, "r") as f:
                        content = f.read()
                        if content != last_content:
                            print(f"File updated: {content}")
                            last_content = content
                            last_mtime = current_mtime
            else:
                last_mtime = None

            time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped monitoring file.")
            break

if __name__ == "__main__":
    main()
