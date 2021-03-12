from typing import Dict, List, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from flask import Flask


def init_commands(app: "Flask"):
    @app.cli.command("load-data")
    def load_data():
        from .db import db
        from .models import Group

        # Create database
        db.create_all()

        # db.session.bulk_insert_mappings(
        #     Group,
        #     [
        #         dict(
        #             id=1,
        #             name="sysadmin",
        #             title="System Administrators",
        #             description=None,
        #         ),
        #         dict(id=2, name="admin", title="Administrators", description=None),
        #         dict(id=3, name="poweruser", title="Power User", description=None),
        #     ],
        # )
        rg = RandomDataGenerator()
        db.session.bulk_insert_mappings(
            Group,
            [
                dict(
                    name=rg.text(1, 1, "gname"),
                    title=rg.text(1, 3, "gtitle"),
                    description=rg.text(2, 10),
                )
                for _ in range(random.randint(10000, 20000))
            ],
        )
        db.session.commit()


class RandomDataGenerator:
    def __init__(self) -> None:
        self.word_list = [x.strip().lower() for x in open("/usr/share/dict/words", "r")]
        self.used_words: Dict[str, List[str]] = {}

    def reset_uniques(self):
        self.used_words = {}

    def text(self, lenmin: int = 2, lenmax: int = 5, unique_tag=None) -> str:
        if unique_tag is not None and unique_tag not in self.used_words:
            self.used_words[unique_tag] = []
        text = ""
        while text == "":
            words = []
            for _ in range(random.randint(lenmin, lenmax)):
                words.append(
                    self.word_list[(random.randint(0, len(self.word_list) - 1))]
                )
            text = " ".join(words)
            if unique_tag is not None and text in self.used_words[unique_tag]:
                text = ""
            elif unique_tag is not None:
                self.used_words[unique_tag].append(text)

        return text