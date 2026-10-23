import logging

from service import check_new_schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def main() -> None:
    logging.info("Начинаем проверку расписания")

    is_new = check_new_schedule()

    if is_new:
        logging.info("Новое расписание обнаружено, уведомление отправлено")
    else:
        logging.info("Нового расписания нет")


if __name__ == "__main__":
    main()
