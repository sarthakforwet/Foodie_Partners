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
