from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Path
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from starlette import status

from app.config_db import engine, local_session
from app.models_hw import Base, Recipe
from app.schemas_hw import AllRecipesOut, OneRecipe

app = FastAPI()

test_data = [
    {
        "name": "fried eggs",
        "time_in_minutes": 10,
        "ingredients": "eggs, water",
        "description": "something",
        "counter": 0,
    },
    {
        "name": "boiled eggs",
        "time_in_minutes": 10,
        "ingredients": "eggs, water",
        "description": "something",
        "counter": 0,
    },
]
test_obj = [Recipe(**test_data[0]), Recipe(**test_data[1])]


async def create_db(local_engine: Engine = engine, base=Base) -> None:
    """
    drops if exists and creates db for testing

    """
    async with local_engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)
        await conn.run_sync(base.metadata.create_all)


@app.on_event("startup")
async def startup() -> None:
    """
    starts create_db func and fills it with test
    data on flask_app start
    :return: None
    """
    await create_db(engine)
    local_session.add_all(test_obj)
    await local_session.commit()
    await local_session.close()


@app.on_event("shutdown")
async def shutdown() -> None:
    """
    on shutting down closes the session and the
    entire connection pool
    :return: None
    """
    await local_session.close()
    await engine.dispose()


@app.get(
    "/recipes/", status_code=status.HTTP_200_OK,
    response_model=List[AllRecipesOut]
)
async def get_meals() -> List[Dict[str, int]]:
    """
    Gets all recipes existing in DB
    in a simple form, having only name, cooking time and popularity
    statistic ordered by popularity. In case of the same popularity
    score less time of cooking
    has priority
    """

    res = await local_session.execute(
        select(Recipe).order_by(Recipe.counter.desc(),
                                Recipe.time_in_minutes.desc())
    )
    await local_session.close()
    return res.scalars().all()


@app.put(
    "/recipes/{recipe_id}", status_code=status.HTTP_200_OK,
    response_model=OneRecipe
)
async def get_meal_by_id(
        recipe_id: Optional[int] = Path(...,
                                        title="id to get a recipe from db",
                                        gt=0)
) -> Dict[str, int]:
    """
    Gets one recipy by it's id and increases the recipe counter

    :param recipe_id: recipe id
    """
    async with local_session.begin():
        res = await local_session.execute(
            select(Recipe).where(Recipe.id == recipe_id))
        res_1 = res.scalar()
        print(res_1)

        new_counter = res_1.counter + 1
        q = (
            update(Recipe)  # type: ignore
            .where(Recipe.id == recipe_id)
            .values(counter=new_counter)
            .execution_options(synchronize_session="fetch")
        )
        await local_session.execute(q)
        await local_session.flush()
        await local_session.commit()

    return res_1


@app.post("/recipes/", status_code=status.HTTP_201_CREATED,
          response_model=OneRecipe)
async def add_recipe(recipe: OneRecipe) -> Recipe:
    """
    adds a new recipe to the DB

    :param recipe: recipe scheme
    """
    async with local_session.begin():
        new_recipe = Recipe(**recipe.dict())
        local_session.add(new_recipe)
        try:
            await local_session.commit()

        except IntegrityError:
            await local_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT("such a name exists")
            )
    return new_recipe
