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
    def __init__(
        self, github_auth_token, github_username, board_name="data", git_url=None
    ) -> None:
        if not self.checkToken(github_auth_token):
            print(f"Unable to authenticate with the given github authentication token")
            exit()

        self.github_auth_token = github_auth_token
        self.github_username = github_username

        data_path = join(abspath(join(__file__, "../")), board_name)
        self.json_path = join(data_path, "data.json")
        print(data_path, self.json_path)

        if isdir(data_path) and isdir(join(data_path, ".git")):
            self.repo = Repo(data_path)
        elif git_url:
            self.repo = Repo.clone_from(git_url, data_path)
        else:
            self.repo = Repo.init(data_path, initial_branch="main")

            headers = {"Authorization": f"Bearer {self.github_auth_token}"}

            # check if the provided github user exists
            if (
                get(
                    f"https://api.github.com/users/{self.github_username}/",
                    headers=headers,
                ).status_code
                != 200
            ):
                print("Github user is invalid")
                exit()

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

            created_repo = f"https://api.github.com/repos/{self.github_username}/BARGE-Kanban-{num}"
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
        return (
            200 == get("https://api.github.com/user/repos", headers=headers).status_code
        )
