from moonshot.src.recipes.recipe_arguments import RecipeArguments

from .... import api as moonshot_api
from ..schemas.recipe_create_dto import RecipeCreateDTO
from ..schemas.recipe_response_model import RecipeResponseModel
from ..services.base_service import BaseService
from ..services.utils.exceptions_handler import exception_handler


class RecipeService(BaseService):
    @exception_handler
    def create_recipe(self, recipe_data: RecipeCreateDTO) -> None:
        """
        Create a new recipe with the given data.

        Args:
            recipe_data (RecipeCreateDTO): Data transfer object containing recipe details.
        """
        moonshot_api.api_create_recipe(
            name=recipe_data.name,
            description=recipe_data.description,
            tags=recipe_data.tags,
            categories=recipe_data.categories,
            datasets=recipe_data.datasets,
            prompt_templates=recipe_data.prompt_templates,
            metrics=recipe_data.metrics,
            attack_modules=recipe_data.attack_modules,
            grading_scale=recipe_data.grading_scale,
        )

    @exception_handler
    def get_all_recipes(
        self, tags: str, categories: str, sort_by: str, count: bool
    ) -> list[RecipeResponseModel]:
        """
        Retrieve all recipes, with optional filters for tags, categories, sorting, and including prompt counts.

        Args:
            tags (str, optional): Filter recipes by tags. If None, no tag-based filtering is applied.
            categories (str, optional): Filter recipes by categories. If None, no category-based filtering is applied.
            sort_by (str, optional): Sort recipes by a specified field. If None, no sorting is applied.
            count (bool, optional): Include the total prompt count in each recipe if True.

        Returns:
            list[RecipeResponseModel]: A list of recipe, filtered and sorted, with optional prompt counts.
        """
        retn_recipes = []
        recipes = moonshot_api.api_get_all_recipe()

        for recipe_dict in recipes:
            recipe = RecipeArguments(**recipe_dict)
            retn_recipe = RecipeResponseModel(recipe=recipe)
            if count:
                retn_recipe.total_prompt_in_recipe = get_total_prompt_in_recipe(recipe)
            retn_recipes.append(retn_recipe)
        if tags:
            retn_recipes = [
                recipe for recipe in retn_recipes if tags in recipe.recipe.tags
            ]
        if categories:
            retn_recipes = [
                recipe
                for recipe in retn_recipes
                if categories in recipe.recipe.categories
            ]
        if sort_by:
            if sort_by == "id":
                retn_recipes.sort(key=lambda x: x.recipe.id)

        return [RecipeResponseModel.model_validate(recipe) for recipe in retn_recipes]

    @exception_handler
    def get_all_recipes_name(self) -> list[str]:
        """
        Retrieve the names of all recipes.

        Returns:
            list[str]: A list of recipe names.
        """
        recipes = moonshot_api.api_get_all_recipe_name()
        return recipes

    @exception_handler
    def get_recipe_by_ids(self, recipe_id: str) -> list[RecipeResponseModel] | None:
        """
        Retrieve recipes by their IDs.

        Args:
            recipe_id (str): A comma-separated string of recipe IDs.

        Returns:
            list[RecipeResponseModel] | None: A list of recipe response models or None if no recipes found.
        """
        retn_recipes = []
        recipe_id_list = recipe_id.split(",")
        for id in recipe_id_list:
            recipe_dict = moonshot_api.api_read_recipe(id)
            recipe = RecipeArguments(**recipe_dict)
            retn_recipe = RecipeResponseModel(recipe=recipe)
            retn_recipe.total_prompt_in_recipe = get_total_prompt_in_recipe(recipe)
            retn_recipes.append(retn_recipe)
        return [RecipeResponseModel.model_validate(recipe) for recipe in retn_recipes]

    @exception_handler
    def update_recipe(self, recipe_data: RecipeCreateDTO, recipe_id: str) -> None:
        """
        Update an existing recipe with new data.

        Args:
            recipe_data (RecipeCreateDTO): Data transfer object containing new recipe details.
            recipe_id (str): The ID of the recipe to update.
        """
        moonshot_api.api_update_recipe(
            rec_id=recipe_id,
            name=recipe_data.name,
            description=recipe_data.description,
            tags=recipe_data.tags,
            datasets=recipe_data.datasets,
            prompt_templates=recipe_data.prompt_templates,
            metrics=recipe_data.metrics,
            attack_modules=recipe_data.attack_modules,
            grading_scale=recipe_data.grading_scale,
        )

    @exception_handler
    def delete_recipe(self, recipe_id: str) -> None:
        """
        Delete a recipe by its ID.

        Args:
            recipe_id (str): The ID of the recipe to delete.
        """
        moonshot_api.api_delete_recipe(recipe_id)


@staticmethod
def get_total_prompt_in_recipe(recipe: RecipeArguments) -> int:
    """
    Calculate the total number of prompts in a recipe.

    This function sums up the number of dataset prompts and then multiplies
    the result by the number of prompt templates if they exist.

    Args:
        recipe (RecipeArguments): The recipe object containing the stats and
                                  prompt templates information.

    Returns:
        int: The total count of prompts within the recipe.
    """
    # Initialize total prompt count
    total_prompt_count = 0

    # Add counts from dataset prompts if available
    datasets_prompts = recipe.stats.get("num_of_datasets_prompts", {})
    total_prompt_count += sum(datasets_prompts.values())

    # If there are prompt templates, scale the total count by the number of templates
    if recipe.prompt_templates:
        total_prompt_count *= len(recipe.prompt_templates)

    return total_prompt_count
