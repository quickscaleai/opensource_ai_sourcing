import numpy as np
import pandas as pd
import re
from typing import Dict
import sklearn
from sklearn.preprocessing import MinMaxScaler

from config import (
    C_REPO_NAME,
    C_ORGA_NAME,
    C_OWNER_NAME,
    C_REPO_STARS,
    GITHUB_REPO_SCORE_FILEPATH,
    C_REPO_LAST_MODIFIED,
)
from collect import GithubCollector

# TODO: down score: nb years since last updated date , nb years since creation date > 8 years
# TODO: tests orga aggreg score : opendp > viadee
# false positive: PhET Interactive Simulations > all repo are for math educational purpose (remove Type Script equality from research ? )

MIN_STARS = 5
BIG_COMPANY_LIST = [
    "Microsoft",
    "Meta Research",
    "Google",
    "BCG Gamma",
    "BCG-Gamma",
    "Amazon",
    "IBM",
    "salesforce",
    "facebookresearch",
    "Netflix",
    "AstraZeneca",
    "DeepMind",
    "PAIR",
    "LinkedIn",
    "tensorflow",
]
PRIORITY_LANGUAGES = ["Python", "C++", "R", "Java", "Julia", "Scala", "MATLAB", "C"]
C_IS_BIG_COMPANY = "is_big_company"
C_IS_PRIORITY_LANGUAGE = "is_priority_language"
C_IS_ABOVE_MIN_STARS = "is_above_min_stars"
C_REPO_YEARS_SINCE_CREATION = "repo_years_since_creation"
C_REPO_YEARS_SINCE_MODIFICATION = "repo_years_since_modification"
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
    C_REPO_YEARS_SINCE_CREATION: -5,
    C_REPO_YEARS_SINCE_MODIFICATION: -5,
}


def add_is_big_company(repositories):

    regex_big_company = "*|".join(BIG_COMPANY_LIST) + "*"
    mask = (
        (
            repositories[C_REPO_NAME].str.contains(
                regex_big_company, na=False, flags=re.IGNORECASE
            )
        )
        | (
            repositories[C_OWNER_NAME].str.contains(
                regex_big_company, na=False, flags=re.IGNORECASE
            )
        )
        | (
            repositories[C_ORGA_NAME].str.contains(
                regex_big_company, na=False, flags=re.IGNORECASE
            )
        )
    )
    return repositories.assign(**{C_IS_BIG_COMPANY: np.where(mask, 1, 0)})


def add_is_priority_language(repositories):

    mask = ~repositories.repo_language.isnull() & (
        repositories.repo_language.isin(PRIORITY_LANGUAGES)
    )
    return repositories.assign(**{C_IS_PRIORITY_LANGUAGE: np.where(mask, 1, 0)})


def add_is_above_min_stars(repositories):
    mask = repositories[C_REPO_STARS] > MIN_STARS
    return repositories.assign(**{C_IS_ABOVE_MIN_STARS: np.where(mask, 1, 0)})


def add_years_since_creation(repositories):
    return repositories.assign(
        **{
            C_REPO_YEARS_SINCE_CREATION: (
                pd.Timestamp.today() - repositories.repo_created_at
            ).dt.days
            / 365
        }
    )


def add_years_since_last_modification(repositories):
    return repositories.assign(
        **{
            C_REPO_YEARS_SINCE_MODIFICATION: (
                pd.Timestamp.today() - repositories[C_REPO_LAST_MODIFIED]
            ).dt.days
            / 365
        }
    )


def add_features(repositories):
    return (
        repositories.pipe(add_is_big_company)
        .pipe(add_is_priority_language)
        .pipe(add_is_above_min_stars)
        .pipe(add_years_since_creation)
        .pipe(add_years_since_last_modification)
    )


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

    return repositories.merge(X[["score"]], left_index=True, right_index=True)


# def simple_aggregation(X):
#     return X.assign(**{
#         C_SCORE:  X.sum(axis=1)
#     })


def save_score(repositories):
    repositories.to_csv(GITHUB_REPO_SCORE_FILEPATH)


if __name__ == "__main__":
    g = GithubCollector()
    repositories = add_features(g.github_repositories)
    repositories = score(repositories, SCORE_FEATURES_WEIGHTS)
    # save_score(repositories)
    candidates = (
        repositories[repositories[C_SCORE] > 0]
        .sort_values(by=C_SCORE, ascending=False)
        .reset_index(drop=True)
    )
    print(
        candidates[candidates[C_IS_BIG_COMPANY] == 0]
        .groupby(["orga_name"])[C_SCORE]
        .sum()
        .sort_values(ascending=False)
        .head(50)
    )
    print(
        candidates[candidates[C_IS_BIG_COMPANY] == 0]
        .groupby(["owner_name", "repo_size"])[C_SCORE]
        .sum()
        .sort_values(ascending=False)
        .head(50)
    )
