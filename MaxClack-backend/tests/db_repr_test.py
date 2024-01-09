import unittest
from sqlalchemy.orm import mapped_column, Mapped
from src.db_config import _BaseModel


class DBTest(unittest.TestCase):
    class IdReprModel(_BaseModel):
        __tablename__ = 'id_repr'
        id: Mapped[int] = mapped_column(primary_key=True)

        def __init__(self, id: int):
            self.id = id

    class SuperReprModel(_BaseModel):
        __tablename__ = 'super_repr'
        my_id: Mapped[int] = mapped_column(primary_key=True)

    class CustomReprModel(_BaseModel):
        __tablename__ = 'custom_repr'
        id: Mapped[int] = mapped_column(primary_key=True)
        username: Mapped[str]

        def __init__(self, id: int, username: str):
            self.id = id
            self.username = username

        def __repr__(self):
            return self._repr_helper(id=self.id, username=self.username)

    def test_default_repr(self):
        # ensure it prints the id in repr format
        self.assertEqual(repr(self.IdReprModel(id=5)), "IdReprModel(id=5)")
        self.assertEqual(repr(self.IdReprModel(id=12)), "IdReprModel(id=12)")

    def test_super_repr(self):
        instance = self.SuperReprModel()
        assert repr(instance).startswith(
            '<db_test.DBTest.SuperReprModel object at ')

    def test_custom_repr(self):
        self.assertEqual(repr(self.CustomReprModel(id=5, username='jqden')),
                         "CustomReprModel(id=5,username='jqden')")
