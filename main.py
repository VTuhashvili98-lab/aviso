from service import load_last_document_id, save_last_document_id


def main():
    save_last_document_id(3379)
    print(load_last_document_id())


if __name__ == "__main__":
    main()
