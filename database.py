import supabase


class DataBaseManager:
    def __init__(self, url, key):
        self.db_instance = supabase.create_client(url, key)

    def getAllUsers(self):
        return self.db_instance.table("Users").select("*").execute()

    def getUserbyId(self, userId):
        return (
            self.db_instance.table("Users")
            .select("*")
            .eq("id", userId)
            .execute()
            .data[0]
        )

    def addUser(self, id, username):
        self.db_instance.table("Users").insert(
            {"id": id, "username": username}
        ).execute()

    def addGame(self, winnerId, loserId):
        self.db_instance.table("Games").insert(
            {"winnerId": winnerId, "loserId": loserId}
        ).execute()

    def getUserWins(self, userId):
        return len(
            self.db_instance.table("Games")
            .select("*")
            .eq("winnerId", userId)
            .execute()
            .data
        )

    def getLobbies(self):
        return self.db_instance.rpc("getlobbies", params=[]).execute().data

    def createLobby(self, userId, userIp, duration):
        self.db_instance.table("Lobbies").insert(
            {"hostId": userId, "hostIp": userIp, "roundDuration": duration}
        ).execute()

    def removeLobby(self, userId):
        self.db_instance.table("Lobbies").delete().eq("hostId", userId).execute()

    def setLobbyInGame(self, userId):
        self.db_instance.table("Lobbies").update({"status": 2}).eq(
            "hostId", userId
        ).execute()

    def getLeaderboard(self):
        return self.db_instance.rpc("getleaderboard", params=[]).execute().data

    def getUserGamesHistory(self, userId):
        return (
            self.db_instance.rpc("getusergameshistory", params=[{"userid": userId}])
            .execute()
            .data
        )
