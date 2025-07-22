from logs.logger import logger
from storage.combine_json import save_all_vacancies
from utils.job_filter import filter_and_score_jobs_from_file


def save_backup_and_filter_jobs():
    """
    Combined function to save all vacancies, make a backup,
    and filter & score the saved jobs.
    """
    try:
        save_all_vacancies()  # backup integrated in this func
        filter_and_score_jobs_from_file()
    except Exception as e:
        logger.error(
            f"Error during save, backup or filtering process: {e}",
            exc_info=True,
        )
