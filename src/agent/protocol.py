from dataclasses import dataclass

VALID_ROLES = {"user", "assistant", "tool"}


@dataclass
class Message:
    role: str
    content: str

    def __post_init__(self):
        # TODO: raise ValueError if self.role is not in VALID_ROLES
        if self.role not in VALID_ROLES:
            raise ValueError

    def to_dict(self) -> dict:
        # TODO: return {"role": ..., "content": ...}
        return {"role": self.role, "content":  self.content}
