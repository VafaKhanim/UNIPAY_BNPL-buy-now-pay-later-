class NotFoundError(Exception):
    def __init__(self, entity: str, entity_id: str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} not found: {entity_id}")


class BusinessRuleError(Exception):
    """Domain business rule violation."""
    pass


class DuplicateError(Exception):
    def __init__(self, field: str):
        super().__init__(f"Already exists: {field}")