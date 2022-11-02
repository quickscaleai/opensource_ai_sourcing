import numpy as np
import pandas as pd
import re

from config import (
    C_REPOSITORY_NAME,
    C_ORGANIZATION_NAME,
    C_OWNER_NAME,
    C_REPOSITORY_STARS,
    C_REPOSITORY_LAST_MODIFIED,
)

MIN_STARS = 20
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
    "pytorch",
    "Capital One",
    "H2O.ai",
    "OpenAI",
    "SAP",
    "Uber",
]

AI_KEYWORDS = [
    "ml",
    "machine learning",
    "ai",
    "deep learning",
    "artificial intelligence",
    "reinforcement learning",
    "language model",
    "scientific",
    "statistics",
    "nlp",
    "computer vision",
    "deep-learning",
    "natural language processing",
    "differential-privacy",
    "differential privacy"
]

PRIORITY_LANGUAGES = ["Python", "C++", "R", "Java", "Julia", "Scala", "MATLAB", "C"]
C_IS_BIG_COMPANY = "is_big_company"
C_IS_PRIORITY_LANGUAGE = "is_priority_language"
C_IS_ABOVE_MIN_STARS = "is_above_min_stars"
C_REPOSITORY_YEARS_SINCE_CREATION = "repo_years_since_creation"
C_REPOSITORY_YEARS_SINCE_MODIFICATION = "repo_years_since_modification"
C_REPOSITORY_CONTAINS_AI_KEYWORDS = "repo_contains_ai_keywords"


def add_is_big_company(repositories: pd.DataFrame) -> pd.DataFrame:

    regex_big_company = "*|".join(BIG_COMPANY_LIST) + "*"
    mask = (
        (
            repositories[C_REPOSITORY_NAME].str.contains(
                regex_big_company, na=False, flags=re.IGNORECASE
            )
        )
        | (
            repositories[C_OWNER_NAME].str.contains(
                regex_big_company, na=False, flags=re.IGNORECASE
            )
        )
        | (
            repositories[C_ORGANIZATION_NAME].str.contains(
                regex_big_company, na=False, flags=re.IGNORECASE
            )
        )
    )
    return repositories.assign(**{C_IS_BIG_COMPANY: np.where(mask, 1, 0)})


def add_is_priority_language(repositories: pd.DataFrame) -> pd.DataFrame:

    mask = ~repositories.repo_language.isnull() & (
        repositories.repo_language.isin(PRIORITY_LANGUAGES)
    )
    return repositories.assign(**{C_IS_PRIORITY_LANGUAGE: np.where(mask, 1, 0)})


def add_is_above_min_stars(repositories: pd.DataFrame) -> pd.DataFrame:
    mask = repositories[C_REPOSITORY_STARS] > MIN_STARS
    return repositories.assign(**{C_IS_ABOVE_MIN_STARS: np.where(mask, 1, 0)})


def add_years_since_creation(repositories: pd.DataFrame) -> pd.DataFrame:
    return repositories.assign(
        **{
            C_REPOSITORY_YEARS_SINCE_CREATION: (
                pd.Timestamp.today() - repositories.repo_created_at
            ).dt.days
            / 365
        }
    )


def add_years_since_last_modification(repositories: pd.DataFrame) -> pd.DataFrame:
    return repositories.assign(
        **{
            C_REPOSITORY_YEARS_SINCE_MODIFICATION: (
                pd.Timestamp.today() - repositories[C_REPOSITORY_LAST_MODIFIED]
            ).dt.days
            / 365
        }
    )


def add_repo_contains_ai_keywords(repositories, ai_keywords=AI_KEYWORDS):
    """based on either repo description or topic description"""

    def construct_regex_from_keywords(ai_keywords):
        return r"\b" + r"\b|\b".join(ai_keywords) + r"\b"

    regex = construct_regex_from_keywords(ai_keywords)
    mask = (
        repositories.repo_description.str.lower().str.contains(
            regex, regex=True, na=False
        )
    ) | (repositories.repo_topics.str.lower().str.contains(regex, regex=True, na=False))
    return repositories.assign(
        **{C_REPOSITORY_CONTAINS_AI_KEYWORDS: np.where(mask, 1, 0)}
    )


def add_features(repositories: pd.DataFrame) -> pd.DataFrame:
    return (
        repositories.pipe(add_is_big_company)
        .pipe(add_is_priority_language)
        .pipe(add_is_above_min_stars)
        .pipe(add_years_since_creation)
        .pipe(add_years_since_last_modification)
        .pipe(add_repo_contains_ai_keywords)
    )
