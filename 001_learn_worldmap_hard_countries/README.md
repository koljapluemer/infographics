# What is the Hardest Country to Find on the World Map

ECGBL 2025 poster submission (insha'allah), based on learning data from my [learn-the-world-map game](https://github.com/koljapluemer/learn-worldmap).


## Tech

- `js` is used only for the inital download of my data from firebase, because that just appeared way less bothersame than python
- `python` is used for subsequent data cleaning and plotting

## Scripts

### 00

Download the data from the firebase store that I used to track learning events of the map learning game in its entirety, as a JSON.

### 01

First Python script. Since the map game switched datasets (i.e. country names and border definitions) at some point, we're making sure to only analyze data after this point, otherwise we'd have weird semi-duplication.