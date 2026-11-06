import json
import logging

import httpx

from service import check_new_schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def main() -> int:
    logging.info("Начинаем проверку расписания")

    try:
        is_new = check_new_schedule()
    except httpx.HTTPStatusError as exc:
        logging.error(
            "API цирка вернул статус %s",
            exc.response.status_code
        )
        return 1

    except httpx.RequestError as exc:
        logging.error(
            "Не удалось выполнить запрос к API цирка: %s",
            type(exc).__name__
        )
        return 1

    except json.JSONDecodeError:
        logging.error("API цирка вернул некорректный JSON")
        return 1

    if is_new:
        logging.info("Новое расписание обнаружено, уведомление отправлено")
    else:
        logging.info("Нового расписания нет")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
