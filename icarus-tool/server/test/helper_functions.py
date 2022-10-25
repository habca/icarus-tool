def create_str_array(old_file: str, new_file: str) -> None:
    """
    Creates an array from a text file.
    This is used from the interpreter.
    >>> from helper_functions import create_str_array
    >>> create_str_array("file_in", "file_out")
    """

    array: list[str] = []
    array.append("[\n")
    with open(old_file, "r") as reader:
        for line in reader:
            line = line.replace("\n", "")
            array.append('"' + line + '",\n')
    array.append("]\n")
    with open(new_file, "w") as writer:
        for line in array:
            writer.write(line)
    print("Completed: " + new_file)


def read_testfile(filename) -> list[str]:
    """
    Creates an array from a text file.
    This is deprecated after using the ddt module.
    """
    with open(filename) as reader:
        data = reader.read()
    expected_output = data.splitlines()
    expected_output = [l for l in expected_output if l != ""]
    expected_output[:1] = []  # Remove first line.
    # Remove comments which clarify user interactions.
    expected_output = [l for l in expected_output if not l.startswith("#")]
    return expected_output
