import discord
import requests

def cocktail():
    """
        Makes an API call to receive a random cocktail. It then checks if the cocktail can fit within the appointent embed size.
        If it figures the ingredients are valid, it'll then organize them into a discord embed. This discord embed is then wrapped up and returned to sender.


    Returns:
        Embed (discord.Embed): The cocktail formatted in a discord embed.
    """
    #Make the API call
    URL = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    valid_drink = False
    response = requests.get(URL)
    data = response.json()
    
    #Decides if the cocktail is valid.
    while not valid_drink:
        tempdata = response.json()
        ing1 = tempdata['drinks'][0]['strIngredient1']
        ing2 = tempdata['drinks'][0]['strIngredient2']
        ing3 = tempdata['drinks'][0]['strIngredient3']

        mes1 = tempdata['drinks'][0]['strMeasure1']
        mes2 = tempdata['drinks'][0]['strMeasure2']
        mes3 = tempdata['drinks'][0]['strMeasure3']

        if (ing1 != None) and (ing2 != None) and (ing3 != None) and (mes1 != None) and (mes2 != None) and (mes3 != None):
            data = response.json()
            valid_drink = True
        else:
            response = requests.get(URL)
    
    #Save the cocktail info as variables
    name = data['drinks'][0]['strDrink'].lower()
    category= data['drinks'][0]['strCategory'].lower()
    instructions = data['drinks'][0]['strInstructions']
    
    ing1 = data['drinks'][0]['strIngredient1']
    ing2 = data['drinks'][0]['strIngredient2']
    ing3 = data['drinks'][0]['strIngredient3']

    mes1 = data['drinks'][0]['strMeasure1']
    mes2 = data['drinks'][0]['strMeasure2']
    mes3 = data['drinks'][0]['strMeasure3']
    
    image = data['drinks'][0]['strDrinkThumb']

    an = 'an'
    if (category[0] != 'a') and (category[0] != 'e') and (category[0] != 'o') and (category[0] != 'i') and (category[0] != 'u'):
        an = 'a'

    #Formats as an embed. 
    embed=discord.Embed(title=f"{name.title()}", 
                        description=f"**-**{mes1} {ing1} \n **-** {mes2} {ing2} \n **-** {mes3} {ing3}\n ... And more \n \n \n **Instructions:** \n {instructions}", color=0xee00ff)
    embed.set_author(name=f"{category.title()}")
    embed.set_thumbnail(url=f"{image}")

    return embed