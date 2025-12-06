from src import fileactions


def test_get_extension():
    res = fileactions.get_extension("src/prompt.txt")
    assert res == ".txt"
    res = fileactions.get_extension("src/prompts/prompt.txt")
    assert res == ".txt"
    res = fileactions.get_extension("src/prompt.txt.md")
    assert res == ".md"


def test_get_file_hash():
    hash1 = fileactions.get_file_hash("./src/tests/test.txt")
    hash2 = fileactions.get_file_hash("./src/tests/test2.txt")
    assert hash1 == hash2
