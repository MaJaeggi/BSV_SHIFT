
#Libraries
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from os import path, makedirs
import argparse
import Country_Comp_Year

# set which country and competition we want to use in Country_Comp_Year.py
from Country_Comp_Year import country,competition,Season2010,Season2011,Season2012,Season2013,Season2014,Season2015, Season2016,Season2017,Season2018,Season2019,Season2020,Season2021,Season2022,CurrentSeason

#set the date of the match we want to predict (pseudo code for now)
#date = today + 24 hours from now

#create an empty df for later use
df=''

#For any occassions whent he webscraber needs to be made to wait a certain number of seconds for a page to load
element_to_wait_for = 'your-class-name'
wait_time = 10

# Setting up webdriver
service = Service()
options = webdriver.ChromeOptions()
#creating the driver oobject
driver = webdriver.Chrome(service = service, options = options)

# Check if 'data.csv' exists in the current directory
if path.exists("2010-2022 Historical Data.csv"):
    # Load data from the existing file
    data = pd.read_csv("2010-2022 Historical Data.csv")
    print("Data loaded from existing csv file. Delete this file inside the 'Betfair API' folder if you want to download the data again")
else:
    #Creating a function to scrape season statistics
    def scrapeseason(country, comp, season):
        # output what the function is attempting to do.
        print("Scraping:", country, comp, str(season)+"-"+str(season+1))
        baseurl = "http://www.soccerpunter.com/soccer-statistics/"
        
        if season <= 2018:

            print("Executing process for seasons 2018 or earlier")
            scrapeaddress = (baseurl + country + "/" + comp.replace(" ", "-").replace("/", "-") + "-"
                                + str(season) + "-" + str(season + 1) + "/results")
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
                    
        
        elif season >= 2019:

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
        
        else:
            print("something is wrong with the function for web scraping each season") 

        return df
    
    #the final section for compiling the data
    seasondata2010 = scrapeseason(country, competition, Season2010)
    seasondata2011 = scrapeseason(country, competition, Season2011)
    seasondata2012 = scrapeseason(country, competition, Season2012)
    seasondata2013 = scrapeseason(country, competition, Season2013)
    seasondata2014 = scrapeseason(country, competition, Season2014)
    seasondata2015 = scrapeseason(country, competition, Season2015)
    seasondata2016 = scrapeseason(country, competition, Season2016)
    seasondata2017 = scrapeseason(country, competition, Season2017)
    seasondata2018 = scrapeseason(country, competition, Season2018)
    seasondata2019 = scrapeseason(country, competition, Season2019)
    seasondata2020 = scrapeseason(country, competition, Season2020)
    seasondata2021 = scrapeseason(country, competition, Season2021)
    seasondata2022 = scrapeseason(country, competition, Season2022)

    # combine our data to one frame
    data = pd.concat([seasondata2010, seasondata2011,seasondata2012,
                      seasondata2013,seasondata2014,seasondata2015,
                      seasondata2016,seasondata2017,seasondata2018,seasondata2019,
                      seasondata2020,seasondata2021,seasondata2022])
    data.reset_index(inplace=True, drop=True)

    # save to file so we don't need to scrape multiple times
    data.to_csv("2010-2022 Historical Data.csv")


# def updatecompetitiondata(country, comp, startseason, datapath):
#     filename = datapath + country + "-" + comp.replace(" ", "-").replace("/", "-") + ".csv"
#     currentseason = datetime.date.today().year
#     todaysdate = datetime.date.today().strftime("%Y-%m-%d")

#     # load (or scrape) our current data
#     currentdata = getcompetitiondata(country, comp, startseason, datapath)

#     # scrape the latest data for this competition
#     latestdata = scrapeseason(country, comp, currentseason)

#     # get index of games that we want to update - homescore will be -1 and date will be today or earlier
#     updateneeded = currentdata.loc[currentdata["homeScore"] < 0].loc[currentdata["date"] <= todaysdate].index.values

#     # for each game in the index
#     for i in updateneeded:
#         # get the date and hometeam
#         gamedate = currentdata.ix[i, "date"]
#         hometeam = currentdata.ix[i, "homeTeam"]

#         # find same date and hometeam in the update dataframe and get the home & away scores
#         homescore = latestdata.loc[latestdata["date"] == gamedate].loc[latestdata["homeTeam"] == hometeam, "homeScore"]
#         awayscore = latestdata.loc[latestdata["date"] == gamedate].loc[latestdata["homeTeam"] == hometeam, "awayScore"]

#         # store the updated scores in our currentdata
#         currentdata.ix[i, "homeScore"] = homescore.values[0]
#         currentdata.ix[i, "awayScore"] = awayscore.values[0]

#     # save to file
#     currentdata.to_csv("Current Season Update.csv")
#     return currentdata