import discord
import requests
import logging

logger = logging.getLogger(__name__)

#Makes the API request.
def _make_request(url: str) -> dict | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
        else:
            logger.error(f"Non-JSON response from {url}: {response.headers.get('Content-Type')}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def get_cocktail_embed() -> discord.Embed | None:
    #Fetches a random cocktail and formats it into an embed.
    url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    logger.debug(f"Requesting cocktail from {url}")
    data = _make_request(url)

    if not data or 'drinks' not in data or not data['drinks']:
        logger.error("Failed to fetch or parse cocktail data.")
        return None

    try:
        drink = data['drinks'][0]
        name = drink.get('strDrink', 'Unknown Cocktail')
        category = drink.get('strCategory', 'Unknown Category')
        instructions = drink.get('strInstructions', 'No instructions available.')
        image_url = drink.get('strDrinkThumb')

        ingredients = []
        for i in range(1, 16):
            ingredient = drink.get(f'strIngredient{i}')
            measure = drink.get(f'strMeasure{i}')
            if ingredient:
                ingredients.append(f"**-** {measure.strip() if measure else ''} {ingredient.strip()}")
            else:
                break

        ingredients_text = "\n".join(ingredients) if ingredients else "No ingredients listed."
        
        if not ingredients:
             logger.warning(f"Cocktail '{name}' fetched with no ingredients.")

        embed = discord.Embed(
            title=name.title(),
            description=f"**Ingredients:**\n{ingredients_text}\n\n**Instructions:**\n{instructions}",
            color=0xDA70D6 # Orchid
        )
        embed.set_author(name=category.title())
        if image_url:
            embed.set_thumbnail(url=image_url)
        
        logger.info(f"Successfully generated embed for cocktail: {name}")
        return embed

    except Exception as e:
        logger.error(f"Error processing cocktail data: {e}", exc_info=True)
        return None
