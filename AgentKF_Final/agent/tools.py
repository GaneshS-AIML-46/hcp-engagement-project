
# ============================================================
# AgentKF - AGENT TOOLS
# ============================================================

class HCPProfileTool:
    """
    Tool used to retrieve information about an HCP.
    """

    def __init__(self, hcp_data):
        self.hcp_data = hcp_data

    def run(self, hcp_id):

        for hcp in self.hcp_data:

            if str(hcp["hcp_id"]) == str(hcp_id):
                return hcp

        return None


class EngagementHistoryTool:
    """
    Tool used to retrieve previous engagement history.
    """

    def __init__(self, history_data):
        self.history_data = history_data

    def run(self, hcp_id):

        history = []

        for record in self.history_data:

            if str(record["hcp_id"]) == str(hcp_id):
                history.append(record)

        return history


class ChannelScoreTool:
    """
    Tool used to retrieve predicted performance
    for different engagement channels.
    """

    def __init__(self, channel_data):
        self.channel_data = channel_data

    def run(self, hcp_id):

        channels = []

        for record in self.channel_data:

            if str(record["hcp_id"]) == str(hcp_id):
                channels.append(record)

        # Sort from highest probability to lowest
        channels.sort(
            key=lambda x: float(
                x.get("probability", 0)
            ),
            reverse=True
        )

        return channels
