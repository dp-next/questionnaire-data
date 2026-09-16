from dotenv import load_dotenv


def load_env_vars() -> None:
    """Load the environment variables.

    First, env vars are loaded from the shared project folder on GenomeDK.
    Then, they are overwritten by values from the local .env file (if this exists).
    """
    load_dotenv("/faststorage/project/sdca-dpnext-study/env/.quest-env")
    load_dotenv(".env", override=True)
