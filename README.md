# Informed Voter

This is informed voter; a website designed to quickly give you access to US goverment official's voting records. The website was designed for individuals who want to quickly and easily navigate through daily, or past government voting records. Users may also create an account to add govermnent members to their homepage for quick access, however an account is not necessary to use the website.

The url for informed voter can be found below
http://informed-voter.herokuapp.com/

## Features

v1 of informed voter allows users to search current congress or senate members and look at their daily vote records. Each individual vote will contain a card with relevant information pertaining to that government member's actions in regards to the vote/bill. Inside each card, there can be found an id-link to navigate to a page where users can see a detailed view of that bill, vote, nomination, etc. In addition, users can navigate to an individual government member's page where they can view contact info for the chosen member as well as links to their Youtube, Facebook, and Twitter social media accounts. Where available, users can click on a contact link for the chosen government memeber if they wish to contact them and they will be redirected to that government member's official contact page.

If a user wishes to search for bills by keyword, informed voter contains a feature that allows bills to be retrieved by search terms. Results are sorted by most relevant and users can click on each search result's id number link to navigate to a page containing detailed information on the chosen item. Here a user may find items, such as, but not limited to, bill title, bill active state, bill passage status, etc.

For users who create an account, they will be able to follow/favorite government members of their choosing. The favorited/followed government members will appear on the users homepage while they have an active session.

## User Flow

These features were chosen because they provide the most amount of information without the need for a user to navigate between multiple websites to obtain records in regards to government bills, votes, nomiations, etc. A typical users experience will include searching for bills, navigating through the reuslts, and clicking on individual search results to see a detailed view of the selected item. Or, a user will navigate to a specific government member's page and view their most recent votes and contact information.

Users who create an account will have the same access as non-registerd users. A registered user flow will first include navigating to one of the signup links found on the homepage. From there the user will create an account using a unique email, a username, and a password. Users will then be redirected to their homepage. From here they will be able to see the members that they are following and also search for other government members or search for bills by keyword. If a user wishes to favorite/follow a governemnt member they can do so by navigating to the list of government members and clicking the star icon under the "follow" column. Users can unfollow goverment members by clicking on a highlighted star icon either from their homepage, or from the list of government members page.


## API
All information and government records are being provided by the [ProPublica Congress API](https://projects.propublica.org/api-docs/congress-api/)

The data is updated six times daily by the ProPublica API so the data retrieved will be the most recent.

API usage does require key authentication which can be obtained directly from ProPublica.

## Tech Stack

This project was built using the following technologies:
* Python
* PostgreSQL
* Jinja/HTML 
* CSS
* Bootstrap
* Javascript
* Flask
* Heroku

A detailed list of dependencies can be found in the *requirements.txt* file of this repository.

## Continuing features

As of the time of this writing v1 of informed voter is live with the functionality mentioned above. Future features to include:

* Feature to allow search/favorite/follow of past government members no longer in office and their voting records
* Feature to allow registered users to quickly share selected bill, or government member records to user's social media accounts
* Feature to allow inline search of government member's voting activity. Currently this is organized by most recent.
* Feature to follow/favorite specific bills for registered users which will then be included in the user's homepage.