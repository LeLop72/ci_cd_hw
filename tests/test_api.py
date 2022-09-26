from app.main_hw import app
from app.models_hw import Recipe
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

#
engine = create_engine("sqlite:///recipe.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session()

client = TestClient(app)
data_to_add = {
    "name": "soup",
    "time_in_minutes": 60,
    "ingredients": "water, meat, potato, salt",
    "description": "something",
}


def test_get_meals():
    with client:
        response = client.get("/recipes/")
        all_recipes = s.query(Recipe).all()
        assert response.status_code == 200
        assert len(response.json()) == len(all_recipes)


def test_get_meal_by_id():
    with client:
        response = client.put("/recipes/1")
        recipe = s.query(Recipe).filter(Recipe.id == 1).one_or_none()
        recipe_output = {
            "name": recipe.name,
            "time_in_minutes": recipe.time_in_minutes,
            "ingredients": recipe.ingredients,
            "description": recipe.description,
        }
        assert response.status_code == 200
        assert response.json() == recipe_output


def test_add_recipe():
    with client:
        response = client.post("/recipes/", json=data_to_add)
        assert response.status_code == 201
        assert response.json() == data_to_add
