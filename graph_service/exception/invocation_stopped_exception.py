class DeepResearchInvocationStoppedException(Exception):

    def __init__(self, invocation_id: str, message: str):
        self.invocation_id = invocation_id

        super().__init__(
            f"Invocation {invocation_id} has been stopped. {message}"
        )