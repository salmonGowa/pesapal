import os
import hashlib
import shutil


class MiniGit:
    """
    A simplified distributed version control system inspired by Git.
    for Pesapal junior developer role
    features:
    Supports repository initialization, file staging, committing,
    viewing commit history, and cloning. Does not support networking,
    conflict resolution, or rebasing.
    """

    def __init__(self):
        self.repo_dir = ".minigit"
        self.objects_dir = os.path.join(self.repo_dir, "objects")
        self.index_file = os.path.join(self.repo_dir, "index")
        self.head_file = os.path.join(self.repo_dir, "HEAD")

    def init(self):
        """
        Initializes a new MiniGit repository.

        Creates the '.minigit' directory and necessary subdirectories
        and files, such as 'objects', 'index', and 'HEAD'.
        """
        if os.path.exists(self.repo_dir):
            print("Repository already initialized.")
            return

        os.makedirs(self.objects_dir, exist_ok=True)
        with open(self.index_file, "w") as index:
            pass  # Empty index
        with open(self.head_file, "w") as head:
            head.write("main\n")

        print("Initialized empty MiniGit repository.")

    def hash_file(self, filepath):
        """
        Computes the SHA-1 hash of a file's content.

        Args:
            filepath (str): Path to the file.

        Returns:
            str: The SHA-1 hash of the file as a hexadecimal string.
        """
        sha1 = hashlib.sha1()
        with open(filepath, "rb") as file:
            while chunk := file.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    def add(self, filepath):
        """
        Stages a file by hashing its content and saving it as a blob.

        The blob is stored in the `objects` directory, and the file
        metadata is written to the `index`.

        Args:
            filepath (str): Path to the file to be staged.
        """
        if not os.path.exists(filepath):
            print(f"Error: File {filepath} does not exist.")
            return

        file_hash = self.hash_file(filepath)
        blob_path = os.path.join(self.objects_dir, file_hash)

        if not os.path.exists(blob_path):
            shutil.copy(filepath, blob_path)

        with open(self.index_file, "a") as index:
            index.write(f"{filepath} {file_hash}\n")

        print(f"Staged file: {filepath}")

    def commit(self, message):
        """
        Creates a new commit from the staged files in the index.

        Args:
            message (str): Commit message describing the changes.
        """
        if not os.path.exists(self.index_file) or os.path.getsize(self.index_file) == 0:
            print("Error: No changes to commit.")
            return

        with open(self.index_file, "r") as index:
            index_content = index.read()

        commit_hash = hashlib.sha1(index_content.encode()).hexdigest()
        commit_path = os.path.join(self.objects_dir, commit_hash)

        with open(commit_path, "w") as commit_file:
            commit_file.write(f"Message: {message}\n")
            commit_file.write(index_content)

        with open(self.head_file, "r+") as head:
            branch_name = head.read().strip()
            branch_path = os.path.join(self.repo_dir, f"refs_{branch_name}.txt")

            with open(branch_path, "a") as branch_file:
                branch_file.write(f"{commit_hash}\n")

        with open(self.index_file, "w") as index:  # Clear the index
            pass

        print(f"Committed changes with hash: {commit_hash}")

    def log(self):
        """
        Displays the commit history of the current branch.

        Prints each commit hash and its associated message.
        """
        with open(self.head_file, "r") as head:
            branch_name = head.read().strip()
        branch_path = os.path.join(self.repo_dir, f"refs_{branch_name}.txt")

        if not os.path.exists(branch_path):
            print("No commits found.")
            return

        print("Commit history:")
        with open(branch_path, "r") as branch_file:
            for commit_hash in branch_file:
                commit_hash = commit_hash.strip()
                commit_path = os.path.join(self.objects_dir, commit_hash)

                with open(commit_path, "r") as commit_file:
                    message = commit_file.readline().strip()
                    print(f"{commit_hash} - {message}")

    def clone(self, target_dir):
        """
        Clones the repository into a new directory.

        Args:
            target_dir (str): Path to the directory where the clone will be created.
        """
        if os.path.exists(target_dir):
            print(f"Error: Directory {target_dir} already exists.")
            return

        shutil.copytree(self.repo_dir, os.path.join(target_dir, ".minigit"))
        print(f"Cloned repository into {target_dir}")


# Main execution block
if __name__ == "__main__":
    import sys

    mini_git = MiniGit()

    if len(sys.argv) < 2:
        print("Usage: python minigit.py <command> [args...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        mini_git.init()
    elif command == "add" and len(sys.argv) == 3:
        mini_git.add(sys.argv[2])
    elif command == "commit" and len(sys.argv) == 3:
        mini_git.commit(sys.argv[2])
    elif command == "log":
        mini_git.log()
    elif command == "clone" and len(sys.argv) == 3:
        mini_git.clone(sys.argv[2])
    else:
        print("Unknown command or incorrect arguments.")
