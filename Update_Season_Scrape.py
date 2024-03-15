import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from os import path, makedirs

# Setting up webdriver
service = Service()
options = webdriver.ChromeOptions()
#creating the driver oobject
driver = webdriver.Chrome(service = service, options = options)

# set which country and competition we want to use in Country_Comp_Year.py
from Country_Comp_Year import country,competition, CurrentSeason

#Creating a function to scrape season statistics
def scrapeseason(country, comp, season):
    # output what the function is attempting to do.
    print("Scraping:", country, comp, str(season)+"-"+str(season+1))
    baseurl = "http://www.soccerpunter.com/soccer-statistics/"

    print("Executing process for seasons 2019 and later")

    # Map each season to its corresponding five-digit number
    season_numbers = {
    2019: 16036,
    2020: 17420,
    2021: 18378,
    2022: 19734,
    2023: 21646,
    # Add more seasons as needed in the future
    }

    # Use the predefined five-digit number for the season
    five_digit_number = season_numbers.get(season)
    # Construct the url required
    scrapeaddress = f"https://www.soccerpunter.com/results/{five_digit_number}/{country.replace(' ', '-')}-{comp.replace(' ', '-')}-{season}-{season + 1}"
    print("URL:", scrapeaddress)
    print("")

    # scrape the page and create beautifulsoup object
    driver.get(scrapeaddress)
    page = bs(driver.page_source, "lxml")

    # find the main data table within the page source
    maintable = page.find("table", "competitionRanking")

    # seperate the data table into rows
    games = maintable.find_all("tr")

    # create an empty pandas dataframe to store our data
    df = pd.DataFrame(columns=["date", "homeTeam", "homeScore", "awayScore", "awayTeam"])

    idx = 0
    today = datetime.date.today()

    for game in games:

        # these lines filter out any rows not containing game data, some competitions contain extra info.
        try:
            cls = game["class"]
        except:
            cls = "none"
        if ("titleSpace" not in cls and "compHeading" not in cls and
                "matchEvents" not in cls and "compSubTitle" not in cls and cls != "none"):

            datestr = game.find("a").text
            gamedate = datetime.datetime.strptime(datestr, "%d/%m/%Y").date()

            # filter out "extra time", "penalty shootout" and "neutral ground" markers
            hometeam = game.find("td", "teamHome").text
            hometeam = hometeam.replace("[ET]", "").replace("[PS]", "").replace("[N]", "").strip()
            awayteam = game.find("td", "teamAway").text
            awayteam = awayteam.replace("[ET]", "").replace("[PS]", "").replace("[N]", "").strip()

            # if game was played before today, try and get the score
            if gamedate < today:
                scorestr = game.find("td", "score").text

                # if the string holding the scores doesn't contain " - " then it hasn't yet been updated
                if " - " in scorestr:
                    homescore, awayscore = scorestr.split(" - ")

                    # make sure the game wasn't cancelled postponed or suspended
                    if homescore != "C" and homescore != "P" and homescore != "S":
                        # store game in dataframe
                        df.loc[idx] = {"date": gamedate.strftime("%Y-%m-%d"),
                                        "homeTeam": hometeam,
                                        "homeScore": int(homescore),
                                        "awayScore": int(awayscore),
                                        "awayTeam": awayteam}
                        # update our index
                        idx += 1
            else:
                # it's a future game, so store it with scores of -1
                df.loc[idx] = {"date": gamedate.strftime("%Y-%m-%d"),
                                "homeTeam": hometeam,
                                "homeScore": -1,
                                "awayScore": -1,
                                "awayTeam": awayteam}
                idx += 1

    # sort our dataframe by date
    df.sort_values(['date', 'homeTeam'], ascending=[True, True], inplace=True)
    df.reset_index(inplace=True, drop=True)
    print("sorting matches by date...")
    # add a column containing the season, it'll come in handy later.
    df["season"] = season
    print("Adding a 'Season' Column to the dataframe....")
    return df

seasondataCurrent = scrapeseason(country, competition, CurrentSeason)
seasondataCurrent.reset_index(inplace=True, drop=True)
seasondataCurrent.to_csv("Current Season.csv")