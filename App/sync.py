from datetime import datetime
from json import dumps
from os.path import isdir, join, dirname

from git import Repo
from requests import get, post


# https://refactoring.guru/design-patterns/singleton/python/example#example-0
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Syncing(metaclass=SingletonMeta):
    def __init__(self, filename) -> None:
        self.github_auth_token = ""
        self.github_username = ""

        self.data_path = dirname(filename)
        self.json_path = filename

        self.repo = None
        self.connectedRepo = False

    def connectRepo(self) -> None:
        if isdir(self.data_path) and isdir(join(self.data_path, ".git")):
            self.repo = Repo(self.data_path)
        else:
            self.createRepo()
        self.connectedRepo = True

    def createRepo(self) -> None:
        self.repo = Repo.init(self.data_path, initial_branch="main")

        headers = {"Authorization": f"Bearer {self.github_auth_token}"}

        # Iterate to find a repo name that hasn't been taken
        num_not_found = True
        num = 0
        while num_not_found:
            check_repo = get(
                f"https://api.github.com/repos/{self.github_username}/BARGE-Kanban-{num}",
                headers=headers,
            ).status_code
            if check_repo == 404:
                break
            elif check_repo == 401:
                print(
                    f"Unable to authenticate with the given github authentication token"
                )
                exit()
            num += 1

        print("Creating repository")
        # Create the repository
        name = f"BARGE-Kanban-{num}"
        payload = {
            "name": name,
            "description": "Storing data for cloud storage and syncing of the BARGE (https://github.com/RafaelCenzano/BARGE) Kanban board application",
        }

        response = post(
            "https://api.github.com/user/repos",
            headers=headers,
            data=dumps(payload),
        )

        if response.status_code != 201:
            print(
                f"Unable to create GitHub repository, recieved {response.status_code} from GitHub"
            )
            exit()

        created_repo = f"https://github.com/{self.github_username}/BARGE-Kanban-{num}"
        print(f"Created {created_repo}")
        self.repo.create_remote("origin", created_repo)
        self.repo.index.add([self.json_path])
        now = datetime.utcnow().strftime("%-m/%-d/%Y %H:%M:%S")
        self.repo.index.commit(f"Initial commit of tasks {now}")
        self.repo.git.push("--set-upstream", self.repo.remote().name, "main")

    def addToken(self, github_auth_token) -> bool:
        if not self.checkToken(github_auth_token):
            print("Unable to authenticate with the given github authentication token")
            # exit()
            return False
        self.github_auth_token = github_auth_token
        return True

    def addUsername(self, github_username) -> bool:
        if self.github_auth_token == "":
            return False
        headers = {"Authorization": f"Bearer {self.github_auth_token}"}

        # Check if the provided github user exists
        if (
            get(
                f"https://api.github.com/users/{github_username}",
                headers=headers,
            ).status_code
            != 200
        ):
            print("Github user is invalid")
            # exit()
            return False
        self.github_username = github_username
        return True

    def readyToSync(self) -> bool:
        return self.github_auth_token != "" and self.github_username != ""

    def connected(self) -> bool:
        return self.connectedRepo

    def sync(self) -> None:
        print("Syncing")
        if self.repo is not None:
            self.repo.remotes.origin.fetch()
            self.repo.index.add([self.json_path])
            now = datetime.utcnow().strftime("%-m-%-d-%Y %H:%M:%S")
            self.repo.index.commit(f"Update tasks {now}")
            self.repo.remotes.origin.pull(rebase=True)
            self.repo.remotes.origin.push()

    @staticmethod
    def checkToken(github_auth_token: str) -> bool:
        headers = {"Authorization": f"Bearer {github_auth_token}"}
        return (
            200 == get("https://api.github.com/user/repos", headers=headers).status_code
        )
