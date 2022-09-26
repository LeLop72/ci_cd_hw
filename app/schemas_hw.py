from pydantic import BaseModel


class RecipeBase(BaseModel):
    name: str
    time_in_minutes: int


class OneRecipe(RecipeBase):

    ingredients: str
    description: str

    class Config:
        orm_mode = True


class AllRecipesOut(RecipeBase):
    counter: int

    class Config:
        orm_mode = True
