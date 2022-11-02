from github import Github
import pandas as pd

from config import (
    GITHUB_REPOSITORY_FILEPATH,
    TAXONOMY,
    REPOSITORY,
    ATTRIBUTES,
    OWNER,
    ORGANIZATION,
    GITHUB_DATA,
    PREFIX,
    C_REPOSITORY_ID,
    C_REPOSITORY_LAST_MODIFIED,
    GITHUB_TOKEN,
)

# TODO:  Collect repo main contributor if it comes from organiezation
LIMIT_PER_QUERY = 10
N_TOP_CANDIDATES_PER_QUERY = 250


class GithubCollector:
    def __init__(self) -> None:
        self.github = Github(GITHUB_TOKEN)  # ACCESS TOKEN

    @property
    def rate_limit(self):
        return self.github.get_rate_limit()

    @property
    def github_repositories(self):
        """Pre-collected repositories"""

        def cast(repositories):
            repositories.repo_created_at = pd.to_datetime(repositories.repo_created_at)
            repositories[C_REPOSITORY_LAST_MODIFIED] = pd.to_datetime(
                repositories[C_REPOSITORY_LAST_MODIFIED], utc=True
            ).dt.tz_localize(None)
            return repositories

        repositories = pd.read_csv(
            GITHUB_REPOSITORY_FILEPATH, delimiter=",", index_col=0
        )
        return cast(repositories)

    def collect(self):
        """Collect data from Github"""
        data = pd.DataFrame()
        repo_ids = self._get_repo_ids(self.github_repositories)
        print("nb initial repo", len(repo_ids))
        for taxo_category, queries in TAXONOMY.items():
            for query in queries[:LIMIT_PER_QUERY]:
                print(query)

                repositories = self.github.search_repositories(
                    query=query + "+in:readme+in:description"
                )
                try:
                    current_repos = self._collect_data_from_repositories(
                        repositories, repo_ids=repo_ids
                    )
                    print(f"found {len(current_repos)} new repositories")
                # FIXME: list except types
                except Exception as e:
                    print(e)
                    return data

                current_repos["taxo_category"] = taxo_category
                current_repos["query"] = query
                data = pd.concat([data, current_repos], ignore_index=True)
                repo_ids.update(self._get_repo_ids(data))
        return data

    def _get_repo_ids(self, repositories: pd.DataFrame):
        if repositories is None:
            repo_ids = []
        else:
            repo_ids = repositories.repo_id.unique().tolist()
        return {e: None for e in repo_ids}

    def get_dataset_column_names(self, github_data=GITHUB_DATA):
        return [
            data[PREFIX] + column
            for level, data in GITHUB_DATA.items()
            for column in data[ATTRIBUTES]
        ]

    def _collect_data_from_repositories(
        self, repositories, github_data=GITHUB_DATA, repo_ids={}
    ):
        def create_record(entity, properties: list) -> list:
            """
            return a list of properties contained in the entity passed in parameter

            """
            return [getattr(entity, property_) for property_ in properties]

        data = []
        for repo in repositories[:N_TOP_CANDIDATES_PER_QUERY]:
            repo_id = repo.id
            if repo_id in repo_ids:
                continue
            repo_data = create_record(repo, github_data[REPOSITORY].get(ATTRIBUTES))
            owner_data = create_record(repo.owner, github_data[OWNER].get(ATTRIBUTES))
            if repo.organization:
                organization_data = create_record(
                    repo.organization, github_data[ORGANIZATION].get(ATTRIBUTES)
                )
            else:
                # fill with nan
                organization_data = [None] * len(GITHUB_DATA[ORGANIZATION][ATTRIBUTES])
            record = repo_data + owner_data + organization_data
            data.append(record)

        return pd.DataFrame(data, columns=self.get_dataset_column_names())


def consolidate_data(old_data, new_data):
    if old_data.shape[1] != new_data.shape[1]:
        print("can't concat check column shape")
    return pd.concat([old_data, new_data], ignore_index=True)


def save_repositories(repositories: pd.DataFrame) -> None:
    repositories.drop_duplicates(C_REPOSITORY_ID).to_csv(GITHUB_REPOSITORY_FILEPATH)


if __name__ == "__main__":

    g = GithubCollector()
    print(g.rate_limit)
    new_repositories = g.collect()
    repositories = consolidate_data(g.github_repositories, new_repositories)
    print(len(repositories))
    save_repositories(repositories)
