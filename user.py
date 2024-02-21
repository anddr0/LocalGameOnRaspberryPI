from database import DataBaseManager
from values import URL, KEY
from datetime import datetime
from connectionManager import ConnectionManager


class User:
    def __init__(self, userId, port=3000):
        self._database = DataBaseManager(URL, KEY)
        self._id, self._username, self._registrationDate = self._database.getUserbyId(
            userId
        ).values()
        self._gamesHistory = self._database.getUserGamesHistory(userId)
        self._winsCount = len(
            list(filter(lambda game: game["userwin"], self._gamesHistory))
        )
        self._connectionManger = ConnectionManager(port)

    def getId(self):
        return self._id

    def getUsername(self):
        return self._username

    def getRegistrationDate(self):
        return self._registrationDate

    def getGamesHistory(self):
        return self._gamesHistory

    def getWinsCount(self):
        return self._winsCount
