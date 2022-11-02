import numpy as np
import pandas as pd
import re
from typing import Dict
import sklearn
from sklearn.preprocessing import MinMaxScaler

from config import (
    C_REPOSITORY_ID,
    C_REPOSITORY_NAME,
    C_ORGANIZATION_ID,
    C_ORGANIZATION_LOGIN,
    C_ORGANIZATION_NAME,
    C_OWNER_ID,
    C_OWNER_LOGIN,
    C_OWNER_NAME,
    
    GITHUB_SCORE_REPOSITORY_FILEPATH,
    GITHUB_SCORE_ORGANIZATION_FILEPATH,
    GITHUB_SCORE_OWNER_FILEPATH
)
from features import (
    MIN_STARS,
    BIG_COMPANY_LIST,
    PRIORITY_LANGUAGES,
    C_IS_BIG_COMPANY,
    C_IS_PRIORITY_LANGUAGE,
    C_IS_ABOVE_MIN_STARS,
    C_REPOSITORY_YEARS_SINCE_CREATION,
    C_REPOSITORY_YEARS_SINCE_MODIFICATION,
)
from features import add_features

from collect import GithubCollector

# TODO: down score: nb years since last updated date , nb years since creation date > 8 years
# TODO: tests orga aggreg score : opendp > viadee
# false positive: PhET Interactive Simulations > all repo are for math educational purpose (remove Type Script equality from research ? )


C_SCORE = "score"


SCORE_FEATURES_WEIGHTS = {
    "repo_stargazers_count": 20,
    "is_priority_language": 5,
    "repo_forks_count": 5,
    "repo_open_issues_count": 5,
    "repo_size": 3,
    "owner_followers": 3,
    "owner_public_repos": 1,
    # "orga_followers":1,
    # "orga_public_repos":1,
    C_REPOSITORY_YEARS_SINCE_CREATION: -5,
    C_REPOSITORY_YEARS_SINCE_MODIFICATION: -5,
}


def _scale_features(X: pd.DataFrame, features) -> pd.DataFrame:
    scaler = MinMaxScaler()
    return pd.DataFrame(scaler.fit_transform(X), columns=features, index=X.index)


def score(repositories: pd.DataFrame, features_weights: Dict[str, int]) -> pd.DataFrame:
    features = list(features_weights.keys())
    X = repositories[features].copy()
    X = _scale_features(X, features)
    X["score"] = 0
    for feature, weights in SCORE_FEATURES_WEIGHTS.items():
        X["score"] += X[feature] * weights
    repositories = repositories.drop(["score"], axis=1, errors="ignore")
    return repositories.merge(X[["score"]], left_index=True, right_index=True)


from enum import Enum


class GithubEntity(Enum):
    REPOSITORY = 1
    OWNER = 2
    ORGANIZATION = 3


def aggregate_score_per_level(repositories: pd.DataFrame) -> pd.DataFrame:
    """aggregate and store the scores for each levels"""

    level_mapping = {
        GithubEntity.REPOSITORY: [C_REPOSITORY_ID, C_REPOSITORY_NAME, C_IS_BIG_COMPANY],
        GithubEntity.OWNER: [C_OWNER_ID, C_OWNER_LOGIN, C_OWNER_NAME, C_IS_BIG_COMPANY],
        GithubEntity.ORGANIZATION: [C_ORGANIZATION_ID, C_ORGANIZATION_LOGIN,C_ORGANIZATION_NAME, C_IS_BIG_COMPANY],
    }
    scores = {}
    for entity_level, group_columns in level_mapping.items():
        if entity_level == GithubEntity.REPOSITORY:
            scores[entity_level] = repositories[group_columns+[C_SCORE]]
        else:
            repositories[group_columns] = repositories[group_columns].fillna("")
            scores[entity_level] = repositories.groupby(group_columns)[C_SCORE].sum().reset_index()

    return scores


def save_scores(scores_per_level: Dict[GithubEntity, pd.DataFrame]):
    for entity_level, scores in scores_per_level.items():
        scores.sort_values(by=C_SCORE, ascending=False).to_csv(
            eval("GITHUB_SCORE_{}_FILEPATH".format(entity_level.name))
        )


if __name__ == "__main__":
    g = GithubCollector()
    repositories = add_features(g.github_repositories)
    repositories = score(repositories, SCORE_FEATURES_WEIGHTS)
    scores = aggregate_score_per_level(repositories)
    save_scores(scores)
