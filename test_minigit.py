import os
import shutil
import pytest
from minigit import MiniGit


@pytest.fixture
def setup_minigit():
    """
    Pytest fixture to set up a temporary test repository and clean up after tests.
    """
    test_dir = "test_repo"
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)

    minigit = MiniGit()
    minigit.init()

    yield minigit

    os.chdir("..")
    shutil.rmtree(test_dir)


def create_test_file(filename, content="Test content"):
    """
    Helper function to create a test file with given content.

    Args:
        filename (str): Name of the file to create.
        content (str): Content to write to the file.
    """
    with open(filename, "w") as file:
        file.write(content)


def test_init_creates_repository(setup_minigit):
    """
    Tests that the `init` command creates the necessary files and directories.
    """
    assert os.path.isdir(".minigit")
    assert os.path.isdir(setup_minigit.objects_dir)
    assert os.path.isfile(setup_minigit.index_file)
    assert os.path.isfile(setup_minigit.head_file)


def test_add_stages_file(setup_minigit):
    """
    Tests that a file is correctly staged.
    """
    filename = "file1.txt"
    create_test_file(filename)
    setup_minigit.add(filename)

    with open(setup_minigit.index_file, "r") as index:
        staged_files = index.read()

    assert filename in staged_files


def test_commit_creates_commit_object(setup_minigit):
    """
    Tests that committing creates a commit object in the objects directory.
    """
    filename = "file1.txt"
    create_test_file(filename)
    setup_minigit.add(filename)
    setup_minigit.commit("Initial commit")

    objects = os.listdir(setup_minigit.objects_dir)
    assert len(objects) > 0


def test_log_shows_commit_history(setup_minigit):
    """
    Tests that the log command displays the commit history.
    """
    filename = "file1.txt"
    create_test_file(filename)
    setup_minigit.add(filename)
    setup_minigit.commit("Initial commit")

    with open(setup_minigit.head_file, "r") as head:
        branch = head.read().strip()

    branch_path = os.path.join(".minigit", f"refs_{branch}.txt")
    assert os.path.exists(branch_path)

    with open(branch_path, "r") as branch_file:
        commit_hashes = branch_file.read().strip().split("\n")

    assert len(commit_hashes) > 0


def test_clone_creates_new_repository(setup_minigit):
    """
    Tests that the clone command creates a new repository in the target directory.
    """
    clone_dir = "cloned_repo"
    setup_minigit.clone(clone_dir)

    assert os.path.isdir(clone_dir)
    assert os.path.isdir(os.path.join(clone_dir, ".minigit"))


def test_add_nonexistent_file(setup_minigit, capsys):
    """
    Tests that attempting to add a nonexistent file prints an error.
    """
    setup_minigit.add("nonexistent.txt")
    captured = capsys.readouterr()
    assert "Error: File nonexistent.txt does not exist." in captured.out


def test_commit_with_no_changes(setup_minigit, capsys):
    """
    Tests that committing without staged changes prints an error.
    """
    setup_minigit.commit("No changes")
    captured = capsys.readouterr()
    assert "Error: No changes to commit." in captured.out


def test_log_no_commits(setup_minigit, capsys):
    """
    Tests that logging with no commits prints an appropriate message.
    """
    setup_minigit.log()
    captured = capsys.readouterr()
    assert "No commits found." in captured.out


def test_clone_to_existing_directory(setup_minigit, capsys):
    """
    Tests that cloning to an existing directory prints an error.
    """
    os.makedirs("existing_dir")
    setup_minigit.clone("existing_dir")
    captured = capsys.readouterr()
    assert "Error: Directory existing_dir already exists." in captured.out
