from datetime import datetime
from json import dumps
from os.path import abspath, exists, isdir, join

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
    def __init__(self, board_name="data", github_auth_token=None, git_url=None) -> None:
        data_path = join(abspath(join(__file__, "../")), board_name)
        self.json_path = join(data_path, "data.json")
        print(data_path, self.json_path)

        if isdir(data_path) and isdir(join(data_path, ".git")):
            self.repo = Repo(data_path)
        elif git_url:
            self.repo = Repo.clone_from(git_url, data_path)
        else:
            self.repo = Repo.init(data_path, initial_branch="main")
            if not github_auth_token:
                print("Auth token needed")
                exit()

            # TODO: iterate through numbers
            num = 0
            name = f"BARGE-Kanban-{num}"
            payload = {
                "name": name,
                "description": "Storing data for cloud storage and syncing of the BARGE (https://github.com/RafaelCenzano/BARGE) Kanban board application",
            }
            headers = {"Authorization": f"token {github_auth_token}"}

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

            # TODO: Get url of repo created from github
            created_repo = ""
            self.repo.create_remote("origin", created_repo)
            self.repo.index.add([self.json_path])
            now = datetime.utcnow().strftime("%-m/%-d/%Y %H:%M:%S")
            self.repo.index.commit(f"Initial commit of tasks {now}")
            self.repo.git.push("--set-upstream", self.repo.remote().name, "main")

    def sync(self) -> None:
        self.repo.remotes.origin.fetch()
        if self.repo.index.diff("HEAD"):
            self.repo.index.add([self.json_path])
            now = datetime.utcnow().strftime("%-m/%-d/%Y %H:%M:%S")
            self.repo.index.commit(f"Update tasks {now}")
        self.repo.remotes.origin.pull(rebase=True)
        self.repo.remotes.origin.push()

    @staticmethod
    def checkToken(github_auth_token: str) -> bool:
        headers = {"Authorization": f"Bearer {github_auth_token}"}
        return 200 == get("https://api.github.com/user/repos", headers).status_code
