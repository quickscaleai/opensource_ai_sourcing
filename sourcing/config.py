import os

# TOKEN
GITHUB_TOKEN = "YOUR TOKEN HERE"

# FILES
## DATA COLLECTION
GITHUB_REPOSITORY_FILENAME = "query.save.csv"

## SCORES
GITHUB_SCORE_REPOSITORY_FILENAME = "scores.repository.csv"
GITHUB_SCORE_OWNER_FILENAME = "scores.owner.csv"
GITHUB_SCORE_ORGANIZATION_FILENAME = "scores.organization.csv"

# DIRECTORIES
SOURCE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SOURCE_ROOT, "../")

# REPOSITORIES_FILEPATH = ...
DATA_DIR = os.path.join(PROJECT_ROOT, "data/")
GITHUB_REPOSITORY_FILEPATH = os.path.join(DATA_DIR, GITHUB_REPOSITORY_FILENAME)
GITHUB_SCORE_REPOSITORY_FILEPATH = os.path.join(
    DATA_DIR, GITHUB_SCORE_REPOSITORY_FILENAME
)
GITHUB_SCORE_OWNER_FILEPATH = os.path.join(DATA_DIR, GITHUB_SCORE_OWNER_FILENAME)
GITHUB_SCORE_ORGANIZATION_FILEPATH = os.path.join(
    DATA_DIR, GITHUB_SCORE_ORGANIZATION_FILENAME
)

# REPOSITORIES_FILEPATH = ...
# REPOSITORIES_FILEPATH = ...

# TAXONOMY
PRIVACY = "privacy"
FAIRNESS = "fairness"
TRANSPARENCY = "transparency"
MISUSE = "misuse"
SUSTAINABILITY = "sustainability"
RISK_ASSESSMENT = "risk assessment"
ETHICS_AND_LEGAL = "Ethics of scale"


TAXONOMY = {
    PRIVACY: [
        "privacy",
        "data privacy",
        "data protection",
        "differential privacy",
        "privacy attack",
        "privacy protection",
        "information security",
    ],
    FAIRNESS: [
        "fairness",
        "algorithmic bias",
        "bias in AI",
        "gender bias",
        "ethnicity bias",
        "sexual orientation bias",
        "disability",
        "parity",
        "equality",
        "fairness learning",
    ],
    TRANSPARENCY: [
        "ai explainability",
        "Explainable AI",
        "AI interpretability",
        "Model interpretability",
        "transparency AI",
        "model explainability",
        "transparency machine learning",
    ],
    MISUSE: [
        "AI misuse",
        "Adversarial Attacks",
        "Deep Fakes",
        "Fake News",
        "Arming Image Generation",
        "Machine Learning Model Misuse",
        "Language Model misuse",
        "Prompt engineering",
        "AI Safety",
    ],
    SUSTAINABILITY: [
        "AI sustainability",
        "Sustainable AI",
        "AI for Climate",
        "AI carbon emission",
        "ai power consumption",
        "machine learning sustainability",
    ],
    ETHICS_AND_LEGAL: [
        "Ethics of scale AI",
        "AI regulation",
        "AI Robots rights",
        "AI Legality",
        "ethics ai",
    ],
}

# CONSTANT NAMES
PREFIX = "prefix"
REPOSITORY = "repository"
OWNER = "owner"
ORGANIZATION = "organization"
ATTRIBUTES = "attributes"

# GITHUB DATA COLLECTION
GITHUB_DATA = {
    REPOSITORY: {
        PREFIX: "repo_",
        ATTRIBUTES: [
            "id",
            "full_name",
            "stargazers_count",
            "watchers_count",
            "description",
            "topics",
            "forks_count",
            "language",
            "visibility",
            "subscribers_count",
            "open_issues_count",
            "created_at",
            "last_modified",
            "has_projects",
            "has_wiki",
            "has_downloads",
            "size",
            "raw_data",
        ],
    },
    OWNER: {
        PREFIX: "owner_",
        ATTRIBUTES: [
            "id",
            "name",
            "login",
            "type",
            "bio",
            "company",
            "role",
            "email",
            "followers",
            "following",
            "location",
            "total_private_repos",
            "public_repos",
            "team_count",
            "twitter_username",
            "created_at",
            "updated_at",
            "raw_data",
        ],
    },
    ORGANIZATION: {
        PREFIX: "orga_",
        ATTRIBUTES: [
            "id",
            "name",
            "login",
            "type",
            "description",
            "company",
            "email",
            "followers",
            "following",
            "location",
            "total_private_repos",
            "public_repos",
            "collaborators",
            "created_at",
            "updated_at",
            "blog",
            "raw_data",
        ],
    },
}

# COLUMNS
C_REPOSITORY_ID = GITHUB_DATA[REPOSITORY][PREFIX] + "id"
C_REPOSITORY_NAME = GITHUB_DATA[REPOSITORY][PREFIX] + "full_name"
C_ORGANIZATION_ID = GITHUB_DATA[ORGANIZATION][PREFIX] + "id"
C_ORGANIZATION_NAME = GITHUB_DATA[ORGANIZATION][PREFIX] + "name"
C_ORGANIZATION_LOGIN = GITHUB_DATA[ORGANIZATION][PREFIX] + "login"
C_OWNER_ID = GITHUB_DATA[OWNER][PREFIX] + "id"
C_OWNER_NAME = GITHUB_DATA[OWNER][PREFIX] + "name"
C_OWNER_LOGIN = GITHUB_DATA[OWNER][PREFIX] + "login"
C_REPOSITORY_STARS = GITHUB_DATA[REPOSITORY][PREFIX] + "stargazers_count"
C_REPOSITORY_LAST_MODIFIED = GITHUB_DATA[REPOSITORY][PREFIX] + "last_modified"
