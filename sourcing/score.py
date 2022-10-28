
import numpy as np 
import pandas as pd  
import re
from typing import List
import sklearn
from sklearn.preprocessing import MinMaxScaler

from config  import C_ORGA_NAME, C_OWNER_NAME, C_REPO_STARS
from collect import GithubCollector

MIN_STARS = 5
BLACK_LIST = ["Microsoft","Meta Research", "Google", "BCG Gamma", "BCG-Gamma","Amazon", "IBM", "salesforce",
                 "facebookresearch", "Netflix", "AstraZeneca", "DeepMind", "PAIR", 
                 ]
PRIORITY_LANGUAGES = ["Python", "C++", "R", "Java", "TypeScript", "Julia", "Scala", "MATLAB", "C" ]
C_IS_BIG_COMPANY = "is_big_company"
C_IS_PRIORITY_LANGUAGE = "is_priority_language"
C_IS_ABOVE_MIN_STARS = "is_above_min_stars"
C_REPO_YEARS_SINCE_CREATION = "repo_years_since_creation"
C_SCORE = "score"

SCORE_FEATURES = ["repo_stargazers_count", "repo_forks_count", "repo_size", "owner_followers", "owner_public_repos"]


def add_is_big_company(repositories):

    regex_black_list = "*|".join(BLACK_LIST) + "*"
    mask = (
        (repositories[C_ORGA_NAME].str.contains(regex_black_list, na=False, flags=re.IGNORECASE))
            | (repositories[C_OWNER_NAME].str.contains(regex_black_list, na=False, flags=re.IGNORECASE ))
            ) 
    return repositories.assign(**{C_IS_BIG_COMPANY: np.where(mask, 1, 0)})

def add_is_priority_language(repositories):
    
    mask = (
        ~repositories.repo_language.isnull()
        & (repositories.repo_language.isin(PRIORITY_LANGUAGES))
    )
    return repositories.assign(
        **{
            C_IS_PRIORITY_LANGUAGE: np.where(mask, 1, 0)
        }
    )

def add_is_above_min_stars(repositories): 
    mask = repositories[C_REPO_STARS] > MIN_STARS
    return repositories.assign(
        **{
            C_IS_ABOVE_MIN_STARS: np.where(mask, 1, 0)
        }
    )

def add_years_since_creation(candidates):
    return candidates.assign(
        **{
        "repo_years_since_creation":(pd.Timestamp.today() - candidates.repo_created_at).dt.days/365
    }
    )
    
def add_features(repositories):
    return repositories.pipe(
                add_is_big_company
            ).pipe(
                add_is_priority_language
            ).pipe(
                add_is_above_min_stars
            ).pipe(
                add_years_since_creation
            )

class GithubRepoScorer():

    def __init__(self, features: List[str]) -> None:
        self.features = features

    def _scale_features(self, X: pd.DataFrame) -> pd.DataFrame:
        scaler = MinMaxScaler()
        return pd.DataFrame(scaler.fit_transform(X), columns=self.features, index=X.index)
    
    def score(self, repositories: pd.DataFrame) -> pd.DataFrame:
        X = repositories[self.features].copy()
        X = self._scale_features(X)
        X["score"] = X.sum(axis=1)
        return repositories.merge(X[["score"]], left_index=True, right_index=True)
        
    def simple_aggregation(X):
        return X.assign(**{
            C_SCORE:  X.sum(axis=1)
        })





if __name__ == '__main__':
    g = GithubCollector()
    repositories = add_features(g.github_repositories)
    scorer = GithubRepoScorer(SCORE_FEATURES)
    repositories = scorer.score(repositories)
    print(repositories[repositories[C_SCORE] > 0].sort_values(by=C_SCORE, ascending=False))