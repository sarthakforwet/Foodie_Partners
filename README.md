# Foodie_Partners
An application which helps people find their foodie partner!

## Features
- Find a Foodie-Partner
- Search Restaurants based on Location and Rating

# Project Flow
- Sign In and Sign up Page
- Profile Page: User can add more details about himself and can add his preferences of Cuisines and can also edit them later.
- Then the user have options to Find Match or to Find Restaurants based on their preferences.
- After going to find Match he can update cuisine and then will get 4 foodie-partners to choose from.
- When he goes to Find Restaurants he will have to enter the location and based on it he will get suggestions of top restaurants based on the rating found from Zomato API.

# Future Scope
- [ ] Location personalization for recommendations.
- [ ] Re-filtering of the recommendations specifically for age and gender preferences.

PS: We maintained pickle files for the model as well as the dataset which would be used for the recommendations.
as it is faster to load files from pickle rather than getting the same data from database. These pickle files are
automatically updated whenever a new user add entries for cuisines+ratings or whenever they update ratings for the cuisines.

# WORK LOCALLY
- All the configurations are managed through the file `config.json`. Changes in it
  reflect to the complete application.

- Note that there is a `db_config.json` file that we made for configuring with
  database and is not present on GitHub (Obviously!) so be sure to create one
  and edit accordingly.

1. Fork the repo.
2. Install dependencies using `requirements.txt`.
3. Right now database is not pushed onto GitHub so consider creating a database
   using [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) or any editor you prefer.
4. After creating of database and installing deps, run `front-end/main.py`. This
   will start a local server for flask and the application will be up for
   working.

For getting a preview of how the model was created or visualizations, please
refer to [BonHacketiet.ipynb]("model_notebook/BonHacketiet.ipynb").

