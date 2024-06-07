import argparse
import os
import re

class GOPOTGenerator:
    POT_HEADER = """msgid ""
msgstr ""
"Project-Id-Version: GOPOT\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8-bit\\n"
    """

    def __init__(self, input_path, output_path, types=None, verbose=False):
        self.input_path = input_path
        self.output_path = output_path
        self.types = types if types else ["tscn", "tres"]
        self.types = [type.lower() for type in self.types]
        self.verbose = verbose

    def generate_pot_file(self):
        if not os.path.exists(os.path.join(self.input_path, "project.godot")):
            print("Invalid input path: project.godot not found in the input directory")
            exit(1)

        file_stack = []

        for root, dirs, files in os.walk(self.input_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.lower().split(".")[-1] in self.types:
                    file_stack.append(file_path)

        translation_stack = {}

        for file_path in file_stack:
            current_path = file_path.replace(self.input_path, "").replace("\\", "/")
            with open(file_path, "r") as file:
                file_lines = file.readlines()
                for line in file_lines:
                    matcher = re.search(r"[Tt][Ee][Xx][Tt] ?= ?\"(.*)\"", line)
                    if not matcher:
                        continue
                    text = matcher.group(1)
                    if not text.startswith("_"):
                        continue
                    if not current_path in translation_stack:
                        translation_stack[current_path] = []
                    for key in translation_stack:
                        if text in translation_stack[key]:
                            break
                    else:
                        translation_stack[current_path].append(text)

        with open(self.output_path, "w") as output_file:
            output_file.write(self.POT_HEADER)
            for key in translation_stack:
                if self.verbose:
                    print(key + ": " + str(len(translation_stack[key])) + (" entries" if len(translation_stack[key]) > 1 else " entry"))
                output_file.write("\n")
                output_file.write("#: " + key + "\n")
                for text in translation_stack[key]:
                    print("- " + text)
                    output_file.write("msgid \"" + text + "\"\n")
                    output_file.write("msgstr \"\"\n")
                    output_file.write("\n")

        print("POT file generated successfully")
        entries = 0
        for key in translation_stack:
            entries += len(translation_stack[key])
        print("Generated " + str(entries) + " entries")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Path to the input directory", required=True)
    parser.add_argument("-o", "--output", help="Path to the output .pot file", required=True)
    parser.add_argument("-t", "--type", help="Extension types to scan", action="append")
    parser.add_argument("-v", "--verbose", help="Enable verbose mode", action="store_true")

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    types = args.type
    types = types if types else ["tscn", "tres"]
    types = [type.lower() for type in types]
    verbose = args.verbose

    generator = GOPOTGenerator(input_path=input_path, output_path=output_path, types=types, verbose=verbose)
    generator.generate_pot_file()

if __name__ == "__main__":
    main()
# Example usage:
# generator = GOPOTGenerator(input_path="/path/to/input", output_path="/path/to/output.pot", types=["tscn", "tres"], verbose=True)
# generator.generate_pot_file()
