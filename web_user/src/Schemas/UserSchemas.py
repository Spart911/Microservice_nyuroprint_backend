from pydantic import BaseModel, conint


class UserInput(BaseModel):
    id_telegram: str
    amount_bonuses: int
    email: str
    password: str


class UserOutput(BaseModel):
    id: int
    amount_bonuses: int
    id_telegram: str
    email: str
    password: str

    class Config:
        orm_mode = True
        from_attributes = True

class UpdatePrivacyPolicyStatus(BaseModel):
    """
    Модель для обновления статуса согласия с политикой конфиденциальности.
    """
    id_telegram: str
    privacy_policy_accepted: bool
