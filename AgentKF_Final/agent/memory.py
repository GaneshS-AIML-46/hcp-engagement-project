
# ============================================================
# AgentKF - MEMORY MANAGER
# ============================================================

import sqlite3
from datetime import datetime


class AgentMemory:


    def __init__(self, database_path):

        self.database_path = (
            database_path
        )

        self._create_table()


    def _connect(self):

        return sqlite3.connect(
            self.database_path
        )


    def _create_table(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_memory (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                hcp_id TEXT NOT NULL,

                objective TEXT,

                action TEXT,

                channel TEXT,

                priority TEXT,

                reason TEXT,

                critic_status TEXT,

                created_at TEXT

            )
            """
        )

        connection.commit()

        connection.close()


    def save(
        self,
        hcp_id,
        objective,
        decision,
        critic
    ):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute(

            """
            INSERT INTO agent_memory (

                hcp_id,
                objective,
                action,
                channel,
                priority,
                reason,
                critic_status,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                str(hcp_id),

                objective,

                decision.get(
                    "action"
                ),

                decision.get(
                    "channel"
                ),

                decision.get(
                    "priority"
                ),

                decision.get(
                    "reason"
                ),

                critic.get(
                    "status"
                ),

                datetime.now().isoformat()

            )

        )


        connection.commit()

        connection.close()


    def get_history(
        self,
        hcp_id,
        limit=10
    ):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute(

            """
            SELECT
                hcp_id,
                objective,
                action,
                channel,
                priority,
                reason,
                critic_status,
                created_at

            FROM agent_memory

            WHERE hcp_id = ?

            ORDER BY id DESC

            LIMIT ?

            """,

            (
                str(hcp_id),
                limit
            )

        )


        rows = cursor.fetchall()

        connection.close()


        columns = [

            "hcp_id",
            "objective",
            "action",
            "channel",
            "priority",
            "reason",
            "critic_status",
            "created_at"

        ]


        return [

            dict(
                zip(
                    columns,
                    row
                )
            )

            for row in rows

        ]


    def get_all(self):

        connection = self._connect()

        cursor = connection.cursor()


        cursor.execute(

            """
            SELECT
                hcp_id,
                objective,
                action,
                channel,
                priority,
                reason,
                critic_status,
                created_at

            FROM agent_memory

            ORDER BY id DESC

            """

        )


        rows = cursor.fetchall()

        connection.close()


        columns = [

            "hcp_id",
            "objective",
            "action",
            "channel",
            "priority",
            "reason",
            "critic_status",
            "created_at"

        ]


        return [

            dict(
                zip(
                    columns,
                    row
                )
            )

            for row in rows

        ]
